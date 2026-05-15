"""HSMB v1 - High-Speed Motion Blur No-Reference IQA metric.

Reference algorithm (frozen for paper resubmission). See PRD section 4.1.
"""

import cv2
import numpy as np


def compute_hsmb(
    image: np.ndarray,
    block_size: int = 64,
    edge_weight: float = 1.5,
    jnb: float = 3.0,
    beta: float = 2.0,
    p_jnb: float = 0.63,
    walk_radius: int = 8,
) -> float:
    """Compute the HSMB v1 score for a grayscale image.

    Higher value (closer to 1) indicates a sharper image; lower value
    indicates stronger motion blur. Defaults are the FROZEN v1 parameters
    used in the resubmission paper - do not change them at call sites.

    Pipeline:
        1. Sobel gradient (gx, gy, gmag).
        2. Partition the image into block_size x block_size blocks.
        3. Active Edge Pixel (AEP) selection per block:
               gmag(p) > mean(gmag_block) * edge_weight.
        4. Quantize the gradient direction at each AEP into 4 bins
           centered on 0, 45, 90, 135 degrees.
        5. For each AEP, sample the intensity profile perpendicular to
           the edge over a window of half-length walk_radius. The Edge
           Visibility Profile (EVP) width is the distance between the
           local intensity maximum and minimum, refined to sub-pixel
           precision via a 3-point parabolic fit.
        6. Map each width w to a blur probability using the JNB Weibull
           CDF:    P_blur = 1 - exp(-(w / jnb) ** beta).
        7. HSMB is the empirical fraction of AEPs with P_blur <= p_jnb,
           i.e. the empirical CDF of the blur-probability distribution
           evaluated at the JNB cut-off p_jnb. Sharper images have most
           AEPs below the cut-off, so HSMB approaches 1.

    Args:
        image: 2-D grayscale image; cast to float32 internally.
        block_size: Square block side length in pixels.
        edge_weight: Multiplier on the per-block mean gradient for AEP gating.
        jnb: Just-Noticeable-Blur reference width in pixels.
        beta: Weibull shape parameter for the blur-probability mapping.
        p_jnb: Blur-probability cut-off used as the CDF query point.
        walk_radius: Half-length of the perpendicular profile window.

    Returns:
        HSMB score in [0.0, 1.0]. Higher means sharper. Returns 0.0 when
        no usable AEP is found (e.g. nearly flat image).

    Raises:
        ValueError: if `image` is not 2-D.
    """
    if image.ndim != 2:
        raise ValueError("image must be a 2-D grayscale array")

    img = image.astype(np.float32)
    H, W = img.shape

    # 1. Sobel gradient.
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    gmag = np.sqrt(gx * gx + gy * gy)

    # 2-3. Per-block AEP mask. Each block is gated by its own mean gradient
    # so that nearly-flat regions do not contribute spurious AEPs.
    aep_mask = np.zeros_like(gmag, dtype=bool)
    for by in range(0, H, block_size):
        for bx in range(0, W, block_size):
            block = gmag[by:by + block_size, bx:bx + block_size]
            block_mean = float(block.mean())
            if block_mean <= 0.0:
                continue
            thr = block_mean * edge_weight
            aep_mask[by:by + block_size, bx:bx + block_size] = block > thr

    # 4. Direction quantization into 4 bins.
    # The bin labels the orientation of the LOCAL GRADIENT, and the walk
    # vector is therefore parallel to the gradient (perpendicular to the
    # underlying edge). The mapping (bin -> (dy, dx)) is:
    #   bin 0: gradient ~horizontal (+/-x) -> walk along x   (0,  1)
    #          [vertical edge]
    #   bin 1: gradient ~+45 degrees       -> walk main-diag (1,  1)
    #          [anti-diagonal edge]
    #   bin 2: gradient ~vertical (+/-y)   -> walk along y   (1,  0)
    #          [horizontal edge]
    #   bin 3: gradient ~-45 degrees       -> walk anti-diag (1, -1)
    #          [main-diagonal edge]
    angle = np.arctan2(gy, gx)
    bin_idx = np.mod(
        np.floor((angle + np.pi / 8.0) / (np.pi / 4.0)).astype(np.int32),
        4,
    )

    ys, xs = np.where(aep_mask)
    if ys.size == 0:
        return 0.0
    dirs = bin_idx[ys, xs]
    walk_steps = np.array([(0, 1), (1, 1), (1, 0), (1, -1)], dtype=np.int32)
    offsets = np.arange(-walk_radius, walk_radius + 1)

    # Nested helper: 3-point parabolic sub-pixel refinement of a discrete
    # extremum index. Falls back to the integer index at array boundaries
    # or when the curvature is degenerate.
    def _refine(prof: np.ndarray, idx: int) -> float:
        if idx <= 0 or idx >= prof.size - 1:
            return float(idx)
        a = float(prof[idx - 1])
        b = float(prof[idx])
        c = float(prof[idx + 1])
        denom = a - 2.0 * b + c
        if abs(denom) < 1e-12:
            return float(idx)
        return float(idx) + 0.5 * (a - c) / denom

    # 5. Sub-pixel edge-width estimation per AEP via monotonicity walk.
    # Starting at the AEP, walk outward in both directions of the
    # perpendicular profile, terminating each side at the first non-
    # monotonic step (i.e. the local intensity extremum that brackets
    # the edge transition). The endpoints are then refined to sub-pixel
    # precision via the 3-point parabolic fit.
    widths: list[float] = []
    center = walk_radius
    for y, x, d in zip(ys, xs, dirs):
        dy, dx = walk_steps[d]
        yy = y + offsets * dy
        xx = x + offsets * dx
        # Skip AEPs whose perpendicular profile would leave the image.
        if (yy < 0).any() or (yy >= H).any() or (xx < 0).any() or (xx >= W).any():
            continue
        profile = img[yy, xx]

        # Determine edge polarity from the local slope at the center.
        slope = float(profile[center + 1] - profile[center - 1])
        if abs(slope) < 1e-8:
            continue
        polarity = 1.0 if slope > 0.0 else -1.0

        # Walk left while the profile keeps decreasing in the polarity
        # direction (i.e. moving deeper into the dark side of the edge).
        left = center
        while left > 0:
            if (float(profile[left - 1]) - float(profile[left])) * polarity < 0.0:
                left -= 1
            else:
                break

        # Walk right while the profile keeps increasing in the polarity
        # direction (deeper into the bright side of the edge).
        right = center
        while right < profile.size - 1:
            if (float(profile[right + 1]) - float(profile[right])) * polarity > 0.0:
                right += 1
            else:
                break

        if right == left:
            continue
        w = abs(_refine(profile, right) - _refine(profile, left))
        if w > 0.0:
            widths.append(w)

    if not widths:
        return 0.0

    # 6. Blur probability via JNB Weibull CDF.
    w_arr = np.asarray(widths, dtype=np.float32)
    p_blur = 1.0 - np.exp(-np.power(w_arr / jnb, beta))

    # 7. HSMB is the empirical CDF of P_blur evaluated at p_jnb.
    return float(np.mean(p_blur <= p_jnb))

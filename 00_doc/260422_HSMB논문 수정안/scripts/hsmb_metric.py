"""
HSMB Metric Implementation
No-Reference Image Quality Assessment for High-Speed Motion Blur

Based on the algorithm described in Section 4 of the manuscript.
"""

import numpy as np
import cv2


def compute_hsmb(
    image: np.ndarray,
    block_size: int = 64,
    edge_weight: float = 1.5,
    jnb: int = 3,
    beta: float = 2.0,
    n_directions: int = 4,
    profile_length: int = 10,
    p_jnb: float = 0.63,
) -> float:
    """
    Compute HSMB metric score for a single image.

    Parameters
    ----------
    image : np.ndarray
        Input image (grayscale or BGR).
    block_size : int
        Block size for local analysis (default: 64).
    edge_weight : float
        Multiplier for mean gradient to determine AEP threshold.
    jnb : int
        Just Noticeable Blur value (pixels).
    beta : float
        Shape parameter for Weibull CDF blur probability.
    n_directions : int
        Number of edge directions (4 or 8).
    profile_length : int
        Max pixels along edge direction for width estimation.
    p_jnb : float
        CDF threshold for final HSMB score (default: 0.63).

    Returns
    -------
    float
        HSMB score (0~1, higher = sharper).
    """
    if image is None or image.size == 0:
        return 0.0

    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    gray = gray.astype(np.float64)
    h, w = gray.shape

    # Sobel gradients
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)

    # Direction setup
    if n_directions == 8:
        dirs = [(0, 1), (1, 1), (1, 0), (1, -1),
                (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    else:
        dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    all_edge_widths = []

    # Block-based analysis
    for by in range(0, h - block_size + 1, block_size):
        for bx in range(0, w - block_size + 1, block_size):
            block_grad = grad_mag[by:by + block_size, bx:bx + block_size]
            block_gray = gray[by:by + block_size, bx:bx + block_size]
            block_gx = grad_x[by:by + block_size, bx:bx + block_size]
            block_gy = grad_y[by:by + block_size, bx:bx + block_size]

            # AEP threshold: mean gradient * edge_weight
            mean_grad = np.mean(block_grad)
            threshold = mean_grad * edge_weight

            if threshold < 1e-6:
                continue

            # Select Active Edge Pixels
            aep_mask = block_grad > threshold
            aep_positions = np.argwhere(aep_mask)

            if len(aep_positions) == 0:
                continue

            # Compute EVP (Edge Variation Parameter) for this block
            aep_grads = block_grad[aep_mask]
            evp = np.mean(aep_grads)

            for py, px in aep_positions:
                # Determine edge direction (max intensity variation)
                best_dir = 0
                best_var = 0.0
                for di, (dy, dx) in enumerate(dirs):
                    ny, nx = py + dy, px + dx
                    if 0 <= ny < block_size and 0 <= nx < block_size:
                        var = abs(block_gray[ny, nx] - block_gray[py, px])
                        if var > best_var:
                            best_var = var
                            best_dir = di

                dy, dx = dirs[best_dir]

                # Build edge profile along direction
                profile = []
                for step in range(1, profile_length + 1):
                    ny = py + dy * step
                    nx = px + dx * step
                    if 0 <= ny < block_size and 0 <= nx < block_size:
                        profile.append(block_gray[ny, nx])
                    else:
                        break

                if len(profile) < 2:
                    continue

                # Estimate edge width using EVP-based interpolation
                center_val = block_gray[py, px]
                profile_arr = np.array(profile)
                diffs = np.abs(profile_arr - center_val)

                # Normalized threshold based on EVP
                norm_threshold = evp * 0.1  # 10% of EVP as minimum variation

                # Find where intensity variation drops below threshold
                edge_width = len(profile)  # default to full profile
                for k, d in enumerate(diffs):
                    if d < norm_threshold:
                        # Sub-pixel interpolation
                        if k > 0:
                            prev_d = diffs[k - 1]
                            if prev_d > norm_threshold:
                                frac = (prev_d - norm_threshold) / (prev_d - d + 1e-10)
                                edge_width = k + frac
                            else:
                                edge_width = k + 1
                        else:
                            edge_width = 1
                        break

                all_edge_widths.append(edge_width)

    if len(all_edge_widths) == 0:
        return 0.0

    edge_widths = np.array(all_edge_widths)

    # Compute blur probability for each AEP (Equation 2)
    # P_blur = 1 - exp(-(w / jnb)^beta)
    p_blur = 1.0 - np.exp(-((edge_widths / jnb) ** beta))

    # Build PDF and CDF (Equation 3)
    # Histogram of blur probabilities
    n_bins = 100
    hist, bin_edges = np.histogram(p_blur, bins=n_bins, range=(0, 1), density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    # CDF
    cdf = np.cumsum(hist * bin_width)

    # Find HSMB score at P_jnb threshold
    idx = np.searchsorted(bin_centers, p_jnb)
    if idx >= len(cdf):
        hsmb_score = cdf[-1]
    elif idx == 0:
        hsmb_score = cdf[0]
    else:
        # Linear interpolation
        frac = (p_jnb - bin_centers[idx - 1]) / (bin_centers[idx] - bin_centers[idx - 1] + 1e-10)
        hsmb_score = cdf[idx - 1] + frac * (cdf[idx] - cdf[idx - 1])

    return float(np.clip(hsmb_score, 0.0, 1.0))


def compute_hsmb_batch(
    image_paths: list[str],
    **kwargs,
) -> list[float]:
    """Compute HSMB scores for a batch of images."""
    scores = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            score = compute_hsmb(img, **kwargs)
            scores.append(score)
        else:
            scores.append(None)
    return scores

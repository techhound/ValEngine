import logging
import os

logger = logging.getLogger(__name__)

def write_csv(df, filename, base_path):
    if df is None:
        raise ValueError("df must not be None")
    if not hasattr(df, "to_csv"):
        raise TypeError("df must have a to_csv() method")
    if not isinstance(filename, str) or not filename:
        raise ValueError("filename must be a non-empty string")
    if not isinstance(base_path, str) or not base_path:
        raise ValueError("base_path must be a non-empty string")

    output_dir = os.path.join(base_path, "processed")

    try:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, filename)
        df.to_csv(path, index=False)
        return path

    except (OSError, PermissionError) as e:
        logger.exception("Failed to write CSV file %s to %s", filename, path)
        raise

    except Exception:
        logger.exception("Unexpected error writing CSV file %s to %s", filename, path)
        raise


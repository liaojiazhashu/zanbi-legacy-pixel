import ichiwatashi as ic
from PIL import Image

def judge_clean(path):
    # 已是透明背景，直接 crop 到 bbox 后 judge
    im = Image.open(path).convert("RGBA")
    bbox = im.getbbox()
    im2 = im.crop(bbox)
    r = ic.judge(im2, anyway=True)
    print("=" * 60)
    print(path)
    print(f"  size={r.width}x{r.height} opaque={r.opaque}")
    print(f"  colours_used={r.colours_used}")
    print(f"  isolated_rate={r.isolated_rate:.3f}  largest_cluster_rate={r.largest_cluster_rate:.3f}  median_cluster={r.median_cluster}")
    print(f"  bbox_fill={r.bbox_fill:.3f}")
    print(f"  outline_variation={r.outline_variation:.3f}  predictability={r.outline_predictability:.3f}  outline_colours={r.outline_colours}")
    print(f"  silhouette_share={r.silhouette_share:.3f}  dither_pixels={r.dither_pixels}")
    print(f"  periodic_class={r.periodic_class}")
    for n in r.notes:
        print(f"  NOTE: {n}")

judge_clean("portraits/boy_v3.png")

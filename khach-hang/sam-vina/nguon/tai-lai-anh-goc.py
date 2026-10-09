import json, urllib.request, urllib.parse, os
from pathlib import Path
B="https://samngoclinhvietnam.com.vn/"
D=Path(__file__).resolve().parent.parent/"anh-goc"; D.mkdir(parents=True,exist_ok=True)
def tai(u,ten):
    duoi=os.path.splitext(u)[1].lower() or ".jpg"
    p=D/(ten+duoi)
    if p.exists(): return p
    url=B+urllib.parse.quote(u,safe="/:")
    d=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
    p.write_bytes(d); return p
ds=json.load(open(Path(__file__).with_name("san-pham-goc.json"),encoding="utf-8"))
for d in ds:
    for i,a in enumerate(d["anh"]):
        if "banner" in a: continue
        tai(a, d["slug"][:40]+("-%d"%(i+1) if i else ""))
cn={"chung-nhan-attp-1":"upload/hinhanh/attp-219-8545.jpg","chung-nhan-attp-2":"upload/hinhanh/attp-223-2113.jpg",
    "chung-nhan-fda":"upload/hinhanh/fda-2027-7684.jpg","chung-nhan-haccp":"upload/hinhanh/haccp-1-4236.jpg",
    "chung-nhan-iso":"upload/hinhanh/iso-sam-1183.jpg","logo":"upload/hinhanh/logosam-9816.png","logo-2":"upload/hinhanh/logo-2-0325.png",
    "banner-sam-ngoc-linh":"upload/hinhanh/sam-ngoc-linh-2101.jpg","banner-ruou-sam":"upload/hinhanh/ruou-sam-ngoc-linh-2558-52850.jpg",
    "banner-khai-truong":"upload/hinhanh/khai-truong-sam-vina-1-3933-89110.jpg","banner-backdrop":"upload/hinhanh/backdrop_final-02---copy-4531.png",
    "banner-tinh-chat":"upload/hinhanh/banner-ke_tinh-chat-snl_98x37.7cm1-1456.png",
    "anh-z1":"upload/hinhanh/z6206105477885_342a7351515890fe7c0f0b407b87da25-5548.jpg","anh-z2":"upload/hinhanh/z6209525049718_337e96cd0369dd2f1727e4aaa0a63f0d-4997.jpg",
    "anh-tien":"upload/hinhanh/hinh-anh-tien-0786.jpg","anh-khach-1":"upload/hinhanh/kien-kh-2-1376.jpg","anh-khach-2":"upload/hinhanh/kien-khach-hang-3-6660.jpg",
    "anh-cuoi":"upload/hinhanh/1783570650222_1484649684581961139_540721639252837800_c812ba7e583081021055f0a1a7a1dfce-0288.jpg"}
for k,v in cn.items():
    try: tai(v,k)
    except Exception as e: print("loi",k,e)
print(len(list(D.iterdir())),"tep")

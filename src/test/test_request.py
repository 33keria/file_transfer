import urllib
from decimal import Decimal

import requests

from configs import settings

if __name__ == "__main__":
    def download_file(url):
        # NOTE the stream=True parameter below
        data = {"filename": "你好.pdf"}
        fp = settings.ROOT_PATH.joinpath("temp/a.pdf")
        url += "?" + urllib.parse.urlencode(data)
        filesize = size = Decimal("0")
        print("开始下载...")
        with requests.post(url, stream=True) as r:
            filesize = Decimal(str(r.headers["filesize"]))
            r.raise_for_status()
            with open(fp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=settings.FILE_CHUNK_SIZE): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk:
                    size += Decimal(str(settings.FILE_CHUNK_SIZE))
                    schedule = size/filesize
                    if schedule > 1:
                        # print("下载即将完成", end="")
                        pass
                    else:
                        print(str(round(schedule * 100, 2)), end="%")
                        print("\r", end="")
                    f.write(chunk)
        print("下载完毕！")
        return fp
    
    download_file("http://127.0.0.1:10001/file/get/")



import uvicorn

from configs import settings


def main():
    uvicorn.run("app:app", host="0.0.0.0", port=settings.PORT)

if __name__ == "__main__":
    main()
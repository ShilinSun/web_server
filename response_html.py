# coding=utf-8
import sys, os, BaseHTTPServer


class ServerException(Exception):
    pass


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    Error_Page = """\
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """

    def send_content(self, page):
        self.send_response(200)

        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page)))

        self.end_headers()
        self.wfile.write(page)

    def do_GET(self):
        try:
            # getcwd()保存当前工作目录
            # self.path请求的相对路径(由BaseHTTPRequestHandler保存)
            full_path = os.getcwd() + self.path

            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found".format(self.path))

            elif os.path.exists(full_path):
                self.handle_file(full_path)

            else:
                raise ServerException("Unkown object '{0}'".format(self.path))

        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, "rb") as reader:
                content = reader.read()
            # 将文件中读取到的内容发送出去
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read:{1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content)


if __name__ == "__main__":
    serverAddress = ('', 8000)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()

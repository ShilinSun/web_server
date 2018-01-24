# coding=utf-8
import BaseHTTPServer,sys,os,subprocess
class ServerException(Exception):
    pass

# test方法判断是否符合该类指定的条件
# act方法为符合条件时执行的条件
# handler是对RequestHandler实例的引用
# 创建脚本文件的条件类
class case_cgi_file(object):
    '''脚本文件处理'''
    def test(self,handler):
        return os.path.isfile(handler.full_path) and \
               handler.full_path.endswith('.py')

    def act(self,handler):
        handler.run_cgi(handler.full_path)


class case_directory_index_file(object):

    def index_path(self,handler):
        return os.path.join(handler.full_path,'index.html')

    def test(self,handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self,handler):
        print(self.index_path(handler))
        handler.handle_file(self.index_path(handler))


class case_no_file(object):
    '''该路径不存在'''

    def test(self,handler):
        return not os.path.exists(handler.full_path)

    def act(self,handler):
        raise ServerException("'{0}' not found".format(handler.full_path))


class case_existing_file(object):
    '''路径为文件'''

    def test(self,handler):
        return os.path.isfile(handler.full_path)

    def act(self,handler):
        handler.handle_file(handler.full_path)


class case_always_fail(object):

    def test(self,handler):
        return True

    def act(self,handler):
        return ServerException("Unknown object '{0}'".format(handler.path))


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    Cases = [case_no_file(),case_cgi_file(),case_existing_file(),case_directory_index_file(),case_always_fail()]

    def do_GET(self):
        try:

            self.full_path = os.getcwd() + self.path

            for case in self.Cases:

                if case.test(self):
                    case.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)

    Error_page = """
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    """

    def send_content(self,page):
        self.send_response(200)
        self.send_header("Content_Type","text/html")
        self.send_header("Content_Length",str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def handle_error(self,msg):
       content = self.Error_page.format(path = self.path,msg = msg)
       self.send_content(content)

    def handle_file(self,full_path):
        try:

            with open(full_path,"rb") as op:
                content = op.read()
            self.send_content(content)
        except IOError as msg:
            msg = "{0} cannot be read {1}".format(self.path,msg)
            self.handle_error(msg)
    def run_cgi(self,full_path):
        data = subprocess.check_output(["python",full_path])
        self.send_content(data)


if __name__ == "__main__":
    serverAddress = ('', 8000)

    server = BaseHTTPServer.HTTPServer(serverAddress,RequestHandler)
    server.serve_forever()
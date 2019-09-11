
import base64

class Base64Util():

    def str_encode(self,str):
        try:
            output = base64.b64encode(str.encode('utf-8')).decode("utf-8")
        except Exception as e:
            print(e)
            output = ''
        return output

    def byte_encode(self,byte):
        try:
            output = base64.b64encode(byte).decode("utf-8")
        except Exception as e:
            print(e)
            output = ''
        return output

    def decode(self,str):
        try:
            output = base64.b64decode(str.encode('utf-8')).decode("utf-8")
        except Exception as e:
            print(e)
            output = ''
        return output
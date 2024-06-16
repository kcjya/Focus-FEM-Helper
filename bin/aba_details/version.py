

import re
import subprocess



class Version(object):
    def __int__(self):
        pass
    def __call__(self, *args, **kwargs):
        try:
            abaqus_details = {}
            result = subprocess.check_output('abaqus information=versions', stderr=subprocess.STDOUT,shell=True)
            v_str = result.decode('utf-8')
            # 使用正则表达式匹配 Official Version 和 Internal Version 后面的内容
            official_version = re.search(r'Official Version: (.*?)\n', v_str).group(1)
            internal_version = re.search(r'Internal Version: (.*?)\n', v_str).group(1)
            abaqus_details["OV"] = official_version
            abaqus_details["IV"] = internal_version

            return abaqus_details
        except Exception as e:
            return e



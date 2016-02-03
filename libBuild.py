#!/usr/bin/python
#coding=utf-8

import os
import sys
import shutil

''' 以下变量根据需要进行更改 '''

## 静态库项目路径
#project_dir = '/Users/ray/Desktop/DacaiLibrary'
#build_dir = 'build'
#
## 目标svn路径
#svn_dir = '/Users/ray/Desktop/DacaiProject3.02'
#
## 项目编译配置
#configuration = 'Debug'
#target_name = 'DacaiLibrary'

# 静态库项目路径
project_dir = '/Users/ray/Desktop/项目/MyStaticLibraryDemo'
build_dir = 'build'

# 目标svn路径
svn_dir = '/Users/ray/Desktop/项目/MyStaticLibraryDemo'

# 项目编译配置
configuration = 'Debug'
target_name = 'MyStaticLibraryDemo'


''' ////////////////////////////////////////////////////////////////// '''



''' 以下变量不需要更改 '''

# 生成的静态库路径
iphoneos_dir = os.path.join(project_dir, os.path.join(build_dir, configuration + '-iphoneos'))
iphonesimulator_dir = os.path.join(project_dir, os.path.join(build_dir, configuration + '-iphonesimulator'))
universal_dir = os.path.join(project_dir, os.path.join(build_dir, configuration + '-universal'))

# 生成的静态库路径
universal_lib = os.path.join(universal_dir, 'lib' + target_name + '.a')

# 全局变量, 错误信息
error_msg = ''

''' ////////////////////////////////////////////////////////////////// '''


# 递归删除目录下的头文件
def delete_hdrs(dir):
    if dir.endswith('.svn'):
        return
    
    if not os.path.exists(dir):
        return
        
    for file in os.listdir(dir):
        real_path = os.path.join(dir, file)
        if os.path.isfile(real_path):
            if file.endswith('.h'):
                os.remove(real_path)
        else:
            delete_hdrs(real_path)
        
# 仅仅拷贝头文件
def copy_hdrs(src_dir, dst_dir):
    if src_dir.find('.svn') > 0:
        return
    
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        
    for file in os.listdir(src_dir):
        src_file = os.path.join(src_dir, file)
        dst_file = os.path.join(dst_dir, file)
        if os.path.isfile(src_file):
            portion = os.path.splitext(dst_file)
            if portion[1] == '.h':
                shutil.copyfile(src_file, dst_file)
        elif os.path.isdir(src_file):
            copy_hdrs(src_file, dst_file)
            

def build_lib():
    global error_msg

    # 生成路径
#        project_file = os.path.join(project_dir, 'DacaiLibrary.xcodeproj')
        project_file = os.path.join(project_dir, 'MyStaticLibraryDemo.xcodeproj')

    iphoneos_lib = os.path.join(iphoneos_dir, 'lib' + target_name + '.a')
    iphonesimulator_lib = os.path.join(iphonesimulator_dir, 'lib' + target_name + '.a')
    
    # shell cmd
    device_cmd = 'xcodebuild -project ' + project_file + ' -target ' + target_name + ' ONLY_ACTIVE_ARCH=NO -configuration ' + configuration + ' -sdk iphoneos BUILD_DIR=' + build_dir + ' BUILD_ROOT=' + build_dir
    simulator_cmd = 'xcodebuild -project ' + project_file + ' -target ' + target_name + ' -configuration ' + configuration + ' -sdk iphonesimulator BUILD_DIR=' + build_dir + ' BUILD_ROOT=' + build_dir
    universal_cmd = 'lipo -create -output ' + universal_lib + ' ' + iphoneos_lib + ' ' + iphonesimulator_lib
    
    # 编译真机版本
    if os.system(device_cmd) != 0:
        error_msg = '编译真机版本失败'
        return False
        
    # 编译模拟器版本
    if os.system(simulator_cmd) != 0:
        error_msg = '编译模拟器版本失败'
        return False
        
    # 合并
    if not os.path.exists(universal_dir):
        os.mkdir(universal_dir)
    
    if os.system(universal_cmd) != 0:
        error_msg = '合并静态库失败'
        return False
        
    print ('\033[1;32;40m')
    print ('生成静态库成功')
    print ('\033[0m')
    
    return True
	
def copy2proj():
    global error_msg
    if not os.path.exists(universal_lib) or not os.path.isfile(universal_lib):
        error_msg = '未找到静态库'
        return False
    if not os.path.exists(svn_dir):
        error_msg = 'svn路径不存在'
        return False
    
    # 拷贝静态库
    shutil.copyfile(universal_lib, os.path.join(svn_dir, 'lib' + target_name + '.a'))
    
    # 删除以前的头文件
    delete_hdrs(svn_dir)
    
    # 拷贝头文件
#    copy_hdrs(os.path.join(project_dir, 'DacaiLibrary'), svn_dir)
copy_hdrs(os.path.join(project_dir, 'MyStaticLibraryDemo'), svn_dir)


    print ('\033[1;32;40m')
    print ('完成拷贝文件')
    print ('\033[0m')
        
    return True
    
def svn_commit():
    global error_msg

    # 当前路径
    current_path = os.getcwd()


    try:
        # 切换到svn目录
        os.chdir(svn_dir)
        
        # 比较差异
        diff_log = os.popen('svn status').read()
    
        # 输出差异
        print ('比较原始差异:')
        print (diff_log)

        change_list = diff_log.split('\n')
        
        if len(change_list) == 0:
            error_msg = '没有修改任何文件'
            return False
            
        # 比较
        cmd_list = []
        for line in change_list:
            if len(line) == 0:
                continue
            file = line[8:]
        
            if line.startswith('?'):
                cmd_list('svn add ' + file)
            elif line.startswith('!'):
                cmd_list('svn del ' + file)
        
        if len(cmd_list):
            print ('增加or删除文件:')
            for cmd in cmd_list:
                os.system(cmd)
        
        print ('最终差异:')
        os.system('svn status')
        
        # 提交修改
        if os.system('svn ci * -m update') != 0:
            error_msg = 'svn 提交失败 '
            return False
            
        print ('\033[1;32;40m')
        print ('svn提交完成')
        print ('\033[0m')
        
    finally:
        os.chdir(current_path)
    
    return True

def main():
    if build_lib() and copy2proj() and svn_commit():
        print ('\033[1;32;40m')
        print ('脚本执行完毕...')
        print ('\033[0m')
    else:
        print ('\033[1;31;40m')
        print (error_msg)
        print ('\033[0m')
        
main()
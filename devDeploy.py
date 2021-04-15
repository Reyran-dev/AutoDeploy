import paramiko
import yaml
import os

# 해당 프로그램을 실행하기 전에, 
# pip install paramiko
# pip install PyYAML
# 두개의 명령어를 TERMINAL에 입력하여 필요한 모듈을 설치한다

# yaml 파일 읽어서 서버 및 디렉토리 정보 가져오기
# yaml 파일구조 :
# dev:
#   svn:
#       frontend: 'C:\directory1\directory2\directory3...'
#       backend: 'C:\directory1\directory2\directory3...'
#   copy: <- 명령어 실행중 배포를 위해 복사할 파일의 위치
#       frontend: 'file/directory1/directory2' <- 현재 py파일 위치가 root directory
#       backend: 'file/directory1/directory2' <- 현재 py파일 위치가 root directory
#   file: <- 명령어 실행중 배포를 위해 복사할 파일
#       local: 'C:\directory1\directory2\directory3...\XXXX.jar'
#       remote: '/directory1/directory2/directory2/..../XXXX.jar' <- linux server directory
#   ssh:
#       server: ['000.000.000.000'] <- server가 여러개일 경우를 대비하여 배열로 for문 사용
#       username: 'id'
#       password: 'password'

#--------------- 변수 설정 영역 -----------------
with open('config.yaml') as f:
    conf = yaml.safe_load(f)

# 개발서버 config
dev = conf['dev']

# svn 위치
svn_frontend = dev['svn']['frontend']
svn_backend = dev['svn']['backend']

# 배포를 위해 복사할 파일 위치(환경설정용 파일)
copy_frontend = dev['copy']['frontend']
copy_backend = dev['copy']['backend']

# 실제 source 파일 위치
file_local = dev['file']['local']
file_remote = dev['file']['remote']

# ssh server path 및 ID, PW
server = dev['ssh']['server']
username = dev['ssh']['username']
password = dev['ssh']['password']

#--------------- 실제 구동 영역 -----------------
def svn_clear(svn_frontend, svn_backend):
    result = False
    print('[svn clear start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')

    try:
        #frontend svn clear
        os.system('svn cleanup' + svn_frontend)

        #backend svn clear
        os.system('svn cleanup' + svn_backend)

        #정상 반환
        result = True
    except Exception as err:
        print(err)
    
    print('[svn clear end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')
    return result
#################################################################################################

def svn_revert(svn_frontend, svn_backend):
    result = False
    print('[svn revert start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')

    try:
        #frontend svn revert
        os.system('svn revert' + svn_frontend)

        #backend svn revert
        os.system('svn revert' + svn_backend)

        #정상 반환
        result = True
    except Exception as err:
        print(err)
    
    print('[svn revert end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')
    return result
#################################################################################################

def svn_update(svn_frontend, svn_backend):
    result = False
    print('[svn update start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')

    try:
        #frontend svn update
        os.system('svn update' + svn_frontend)

        #backend svn update
        os.system('svn update' + svn_backend)

        #정상 반환
        result = True
    except Exception as err:
        print(err)
    
    print('[svn update end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')
    return result
#################################################################################################

def project_build(svn_frontend, svn_backend, copy_frontend, copy_backend):
    result = False
    print('[project build start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')

    try:
        #frontend file copy
        os.system('xcopy /y "' + copy_frontend + '" "' + svn_frontend + '" ' + '/e /k /h')

        #backend file copy
        os.system('xcopy /y "' + copy_backend + '" "' + svn_backend + '" ' + '/e /k /h')

        #backend build
        #frontend build후 필요 파일만 복사한 다음, backend build(해당 내용은 gradle.build 파일에서 확인 가능)
        os.system('cd ' + svn_backend + ' && gradlew build -x test')

        #정상 반환
        result = True
    except Exception as err:
        print(err)
    
    print('[project build end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')
    return result
#################################################################################################

def ssh_connect(server, username, password, file_local, file_remote):
    result = False
    print('[ssh connect start >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')

    try:
        #여기서부터 작업 시작
        print('[ssh connected]')

        #target server의 갯수만큼 for문
        for targetServer in server:
            #ssh server 작업 영역
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
            ssh.connect(targetServer, username=username, password=password)

            print('[sftp file upload start]')
            sftp = ssh.open_sftp()
            sftp.put(file_local, file_remote)
            print('[sftp file upload success]')

            #ssh에서 특정 프로그램 실행 ex) run.sh 파일
            print('[file backup and server restart processing]')
            fileDirectory = '/directory1/directory2/...' #실행시킬 파일의 디렉토리 위치
            fileName = './run.sh'
            stdin, stdout, stderr = ssh.exec_command('cd ' + fileDirectory + ' && ' + fileName)
            print('[file backup and server restart success]')

            #작업 끝나고 ssh 삭제
            ssh.close()
        
        #정상 반환
        result = True
    except Exception as err:
        print(err)
    
    print('[ssh connect end >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>]')
    return result
#################################################################################################

#함수 실행
svn_clear_result = svn_clear(svn_frontend, svn_backend)
svn_revert_result = svn_revert(svn_frontend, svn_backend)
svn_update_result = svn_update(svn_frontend, svn_backend)

project_build_result = project_build(svn_frontend, svn_backend, copy_frontend, copy_backend)

ssh_connect_result = ssh_connect(server, username, password, file_local, file_remote)
a
    Jxb0   ?                   @   s  d dl Z d dlZd dlmZ d dlmZmZ d dlZd dlZd dlZd dl	Z	d dl
mZ d dlmZ d dlZd dlmZ d dlZd dlmZ dZg Zg Zg Zd	Zd
Ze? ZdZe?? Ze?d? e? d? e?!dd? e?"d? e?#? Z$e?#? Z%e?#? Z&e?#? Z'e?#? Z(e?#? Z)e?*e?Z+e+j,ddddd? ej-e+dd?Z.e.j,ddd? ej/e+e$d?Z0e0j,ddd? e0?1?  ej-e+dd?Z2e2j,ddd? ej/e+e%dd?Z3e3j,ddd? ej-e+dd?Z4e4j,ddd? ej/e+e&d?Z5e5j,ddd? ej-e+dd?Z6e6j,ddd? ej/e+e'd?Z7e7j,ddd? e(?8d? ej-e+dd?Z9e9j,dd? ej:e+dd gd!e(d"?Z;e;?<d ? e;j,dd? e)?8d#? ej-e+d$d?Z=e=j,dd? ej:e+d%d&gd!e)d"?Z>e>?<d ? e>j,dd? ej?e+d'ej@d(?ZAeAj,dd)d*? e?Bd+d? e?C?  e$?D? ZEe%?D? ZFe&?D? ZGe'?D? ZHe(?D? d k?rd,Z;ne(?D? dk?r0d Z;e)?D? d&k?rDd-ZIne)?D? d%k?rVd#ZId.ZJd/ZKe;d k?r?ejLejMeKe?NeJ?e?OejP?gd0? n.e;d,k?r?ejLejQeKe?NeJ?e?OejP?gd0? e?ReS?ZTd1d2? ZUd3d4? ZVeWeXd5?d6d7?ZYd8d9? ZZeSd:k?r?eZ?  dS );?    N)?getpass)?load_workbook?Workbook)?
ThreadPool)?Lock)?ttk)?existsz	127.0.0.1zCDP_Neighbors_Detail.xlsx?   ?
   ztk::PlaceWindow . centerZ300x500FzRequired Details?xT)Zpadx?pady?fill?expandz	Username:)?text)r   r   )?textvariablez

Password:?*)r   Zshowz
Core Switch 1:z	
command:ZOffz

Debugging?w)?anchorZOn?readonly)?values?stater   z10.251.131.6z
Jumper ServerzMMFTH1V-MGMTS02ZAR31NOCZSubmit)r   ?command?   )r   r   z-topmost?   z10.251.6.31z	debug.logz5[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s)?level?format?handlersc                 C   s*   zt ?| ? W dS  ty$   Y dS 0 d S )NTF)?	ipaddressZ
ip_address?
ValueError)?ip? r    ??   C:\Users\christopher.davies1\OneDrive - Müller Service GmbH\Documents\Projects\Network-Programmability\Network Mapping\Send Command Function\main.py?ip_check?   s
    
r"   c                 C   s?  t | ?sBt?" t?d| ? d?? W d   ? n1 s40    Y  dS z?t?  t?d| ? ?? W d   ? n1 sn0    Y  t?? }|?t?? ? |j	t
ttd? |?? }tdf}| df}|jd||td?}t?? }|?t?? ? |j	|tt|tttd	? t?" t?d
| ? d?? W d   ? n1 ?s$0    Y  ||dfW S  tjj?y?   t?" t?d| ? d?? W d   ? n1 ?sz0    Y  Y dS  tjj?y?   t?" t?d| ? d?? W d   ? n1 ?s?0    Y  Y dS  ttf?y*   t?" t?d| ? d?? W d   ? n1 ?s0    Y  Y dS  t?y? } zRt?. t?d| ? d?? t?|? ? W d   ? n1 ?st0    Y  W Y d }~dS d }~0 0 d S )Nz(open_session function error: ip Address z= is not a valid Address. Please check and restart the script!?NNFz%Trying to establish a connection to: )?username?password?   zdirect-tcpip)?timeout)r$   r%   Zsockr'   Zauth_timeoutZbanner_timeoutzConnection to IP: z establishedTzAuthentication to IP: z5 failed! Please check your ip, username and password.zUnable to connect to IP: ?!z-Connection or Timeout error occurred for IP: z6Open Session Error: An unknown error occurred for IP: )r"   ?
ThreadLock?log?error?info?paramikoZ	SSHClientZset_missing_host_key_policyZAutoAddPolicyZconnect?jump_serverr$   r%   Zget_transport?local_IP_addressZopen_channelr'   Zssh_exceptionZAuthenticationExceptionZNoValidConnectionsError?ConnectionError?TimeoutError?	Exception)r   ?jump_boxZjump_box_transportZsrc_addressZdestination_addressZjump_box_channel?target?errr    r    r!   ?jump_session?   sV    ?(.
??2222,r6   )r   ?_listc                    s?   t dt? d??dd??r?t| ?\}}}|s.dS |?t?\}}}|?? }|?d?}tdt? d??dd???$}t?	|?? ? ?
|?}W d   ? n1 s?0    Y  ? fdd?|D ?}	|	D ]}
|?|
? q?|??  |??  nt?d	t? d
?? d S )Nz./textfsm/cisco_ios_z.textfsm? ?_r#   zutf-8c                    s   g | ]}t t? j|???qS r    )?dict?zip?header)?.0?entry?Zre_tabler    r!   ?
<listcomp>?   ?    z send_command.<locals>.<listcomp>zThe command: 'zh', cannot be found. Check the command is correct and make sure the TextFSM file exists for that command.)r   r   ?replacer6   Zexec_command?read?decode?open?textfsmZTextFSMZ	ParseText?append?closer*   r+   )r   r7   Zsshr3   Z
connectionr9   ?stdout?f?result?resultsr>   r    r?   r!   ?send_command?   s     

(
rM   c                  C   s4   g } t t| ? t?| ?}t? d?}|j|dd? d S )Nz.xlsxF)?index)rM   ?IPAddr1?npZ	DataFramer   Zto_excel)Zlist_1Zarray?filepathr    r    r!   ?main?   s
    


rR   ?__main__)[r-   rF   r   Zopenpyxlr   r   r   Zlogging?sys?timeZmultiprocessing.poolr   Zmultiprocessingr   ZtkinterZtkr   ZpandasrP   Zos.pathr   r/   ZIP_LISTZHostnames_ListZcollection_of_results?filenamerN   r)   r'   ZTk?root?evalZgeometryZ	resizable?titleZ	StringVarZUsername_varZpassword_varZIP_Address1_varZcommand_varZDebugging_varZJumpServer_varZFrameZSite_details?packZLabelZUsername_labelZEntryZUsername_entryZfocusZpassword_labelZpassword_entryZIP_Address1_labelZIP_Address1_entryZcommand_labelZcommand_entry?setZDebugging_labelZComboboxZ	Debugging?currentZJumpServer_labelZ
JumpServerZButtonZdestroyZSubmit_buttonZ
attributesZmainloop?getr$   r%   rO   r   r.   ZlogfileZ
log_formatZbasicConfigZWARNZFileHandlerZStreamHandlerrI   ?DEBUGZ	getLogger?__name__r*   r"   r6   ?str?listrM   rR   r    r    r    r!   ?<module>   s?   






?

?

??

??
+

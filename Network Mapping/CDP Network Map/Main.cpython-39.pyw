a
    C5�b�/  �                   @   s�  d Z ddlZddlZddlZddlZddlZddlZddlmZ ddl	m
Z
 ddlZddlmZ ddlZdZg Zg Zg ZdZdZe
� Zd	Ze�� Ze�d
� e�d� e�dd� e�d� e�� Ze�� Z e�� Z!e�� Z"e�� Z#e�� Z$e�%e�Z&e&j'ddddd� ej(e&dd�Z)e)j'ddd� ej*e&ed�Z+e+j'ddd� e+�,�  ej(e&dd�Z-e-j'ddd� ej*e&e dd�Z.e.j'ddd� ej(e&dd�Z/e/j'ddd� ej*e&e!d�Z0e0j'ddd� ej(e&dd�Z1e1j'ddd� ej*e&e"d�Z2e2j'ddd� e#�3d� ej(e&dd�Z4e4j'dd� ej5e&ddgd e#d!�Z6e6�7d� e6j'dd� e$�3d"� ej(e&d#d�Z8e8j'dd� ej5e&d$d%gd e$d!�Z9e9�7d� e9j'dd� ej:e&d&ej;d'�Z<e<j'dd(d)� e�=d*d� e�>�  e�?� Z@e �?� ZAe!�?� ZBe"�?� ZCe#�?� dk�r�d+Z6ne#�?� dk�rdZ6e$�?� d%k�r d,ZDne$�?� d$k�r2d"ZDd-ZEd.ZFe6dk�rjejGejHeFe�IeE�e�JejK�gd/� n.e6d+k�r�ejGejLeFe�IeE�e�JejK�gd/� e�MeN�ZOd0d1� ZPd2d3� ZQd4d5� ZRd6d7� ZSd8d9� ZTeNd:k�r�eT�  dS );a  
This script takes in up to two IP Addresses, preferably the core switches, runs the "Show CDP Neighbors Detail"
command and saves the information to a list of dictionaries. Each dictionary is then parsed for the neighbouring
IP Address for each CDP neighbour and saved to a separate list. Another list is used to store the IP Addresses
of those that have been processed so no switch is connected to more than once. Each IP Address in the list
is connected to, up to 10 at a time, to retrieve the same information. This recursion goes on until there are no
more IP Address to connect to. The information is then converted to a numpy array and saved to an Excel spreadsheet.

Threading is used to connect to multiple switches at a time.
Each IP Address is checked to ensure each IP Address is valid.
�    N)�
ThreadPool)�Lock)�ttkz	127.0.0.1�CDP_Neighbors_Detail.xlsx�   �   ztk::PlaceWindow . centerZ300x500FzRequired Details�
   �xT)Zpadx�pady�fill�expandz	Username:)�text)r   r   )�textvariablez

Password:�*)r   Zshowz
Core Switch 1:z
Core Switch 2 (Optional):ZOffz

Debugging�w)�anchorZOn�readonly)�values�stater   z10.251.131.6z
Jumper ServerzMMFTH1V-MGMTS02ZAR31NOCZSubmit)r   Zcommand�   )r   r
   z-topmost�   z10.251.6.31z	debug.logz5[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s)�level�format�handlersc                 C   s*   zt �| � W dS  ty$   Y dS 0 d S )NTF)�	ipaddressZ
ip_address�
ValueError)�ip� r   ��   C:\Users\christopher.davies1\OneDrive - Müller Service GmbH\Documents\Projects\Network-Programmability\Network Mapping\CDP Network Map\Main.py�ip_check�   s
    
r   c                 C   s�  t | �sBt�" t�d| � d�� W d   � n1 s40    Y  dS z�t�  t�d| � �� W d   � n1 sn0    Y  t�� }|�t�� � |j	t
ttd� |�� }tdf}| df}|jd||td�}t�� }|�t�� � |j	|tt|tttd	� t�" t�d
| � d�� W d   � n1 �s$0    Y  ||dfW S  tjj�y�   t�" t�d| � d�� W d   � n1 �sz0    Y  Y dS  tjj�y�   t�" t�d| � d�� W d   � n1 �s�0    Y  Y dS  ttf�y*   t�" t�d| � d�� W d   � n1 �s0    Y  Y dS  t�y� } zRt�. t�d| � d�� t�|� � W d   � n1 �st0    Y  W Y d }~dS d }~0 0 d S )Nz(open_session function error: ip Address z= is not a valid Address. Please check and restart the script!)NNFz%Trying to establish a connection to: )�username�password�   zdirect-tcpip)�timeout)r    r!   Zsockr#   Zauth_timeoutZbanner_timeoutzConnection to IP: z establishedTzAuthentication to IP: z5 failed! Please check your ip, username and password.zUnable to connect to IP: �!z-Connection or Timeout error occurred for IP: z6Open Session Error: An unknown error occurred for IP: )r   �
ThreadLock�log�error�info�paramikoZ	SSHClientZset_missing_host_key_policyZAutoAddPolicyZconnect�jump_serverr    r!   Zget_transport�local_IP_addressZopen_channelr#   Zssh_exceptionZAuthenticationExceptionZNoValidConnectionsError�ConnectionError�TimeoutError�	Exception)r   �jump_boxZjump_box_transportZsrc_addressZdestination_addressZjump_box_channel�target�errr   r   r   �jump_session�   sV    �(.
��2222,r2   c              	      sX  t | �\}}}|sd S t| �}|tv�rDt�|� |�d�\}}}|�� }|�d�}t�L td��$}t	�
|�� � �|�}W d   � n1 s�0    Y  W d   � n1 s�0    Y  � fdd�|D �}|D ]x}	|�� |	d< | |	d< |	d }
|
�d	�\}}}|�� |	d< t�|	� |	d
 tvr�d|	d v r�d|	d vr�t�|	d
 � q�|��  |��  d S )Nzshow cdp neighbors detail�utf-8z5./TextFSM/cisco_ios_show_cdp_neighbors_detail.textfsmc                    s   g | ]}t t� j|���qS r   )�dict�zip�header)�.0�entry��re_tabler   r   �
<listcomp>�   �    z#get_cdp_details.<locals>.<listcomp>�
LOCAL_HOST�LOCAL_IP�DESTINATION_HOST�.�MANAGEMENT_IPZSwitch�CAPABILITIESZHost)r2   �get_hostname�Hostnames_List�append�exec_command�read�decoder%   �open�textfsm�TextFSM�	ParseText�upper�	partition�collection_of_results�IP_LIST�close)r   �sshr/   �
connection�hostname�_�stdout�f�resultr8   r   �head�sep�tailr   r9   r   �get_cdp_details�   s4    




F
r\   c           
   	   C   s�   t | �\}}}|sd S |�d�\}}}|�� }|�d�}zpt�X td��0}t�|�}|�|�}|d d }	W d   � n1 s~0    Y  W d   � n1 s�0    Y  W n   d}	Y n0 |�	�  |�	�  |	S )Nzshow run | inc hostnamer3   z./textfsm/hostname.textfsmr   z	Not Found)
r2   rF   rG   rH   r%   rI   rJ   rK   rL   rQ   )
r   rR   r/   rS   rU   rV   rW   r:   rX   rT   r   r   r   rC   
  s"    



L
rC   c            	      C   s�   t �� } d}t|�}tt�r&t�t�nt�d� tt	�rBt�t	�nt�
d� d}|tt�k r�|t|tt�| � }t||� }|�t|� |}qP|��  |��  tjtg d�d�}d}|j|dd	� t �� }t�
d
||  d�d�� d S )Nr   z9No valid IP Address was found. Please check and try againzNo valid IP Address was found.r   )	r=   r>   Z
LOCAL_PORTr?   ZREMOTE_PORTrA   ZPLATFORMZSOFTWARE_VERSIONrB   )�columnsr   F)�indexzScript finished in z0.4fz seconds)�time�perf_counterr   r   �IPAddr1rP   rE   r&   r'   �IPAddr2r(   �len�min�mapr\   rQ   �join�npZ	DataFramerO   Zto_excel)	�startZthread_countZpool�i�limitZip_addressesZarray�filepath�endr   r   r   �main  s,    ��
rm   �__main__)U�__doc__r)   rJ   r   Zlogging�sysr_   Zmultiprocessing.poolr   Zmultiprocessingr   ZtkinterZtkr   Zpandasrg   r+   rP   rD   rO   �filenamer^   r%   r#   ZTk�root�evalZgeometryZ	resizable�titleZ	StringVarZUsername_varZpassword_varZIP_Address1_varZIP_Address2_varZDebugging_varZJumpServer_varZFrameZSite_details�packZLabelZUsername_labelZEntryZUsername_entryZfocusZpassword_labelZpassword_entryZIP_Address1_labelZIP_Address1_entryZIP_Address2_labelZIP_Address2_entry�setZDebugging_labelZComboboxZ	Debugging�currentZJumpServer_labelZ
JumpServerZButtonZdestroyZSubmit_buttonZ
attributesZmainloop�getr    r!   ra   rb   r*   ZlogfileZ
log_formatZbasicConfigZWARNZFileHandlerZStreamHandlerrV   �DEBUGZ	getLogger�__name__r&   r   r2   r\   rC   rm   r   r   r   r   �<module>   s�   






�

�

��

��

. .

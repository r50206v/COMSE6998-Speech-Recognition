import os
import sys
import glob
import shutil
import datetime
from tqdm import tqdm
from multiprocessing import Pool

currentPath = os.getcwd()
command = currentPath + "/kaldi/tools/sph2pipe_v2.5/sph2pipe -f wav -p -c 1 "
final_script = currentPath + "/convert_to_wav.scp"
dest_path = currentPath + "/org_audio"

try:
    os.remove(final_script)
except OSError:
    pass


# combining tedlium scp
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
sys.stderr.write('[INFO %s] start combining tedlium scp\n' % now)
collectScp = []
for scp in  glob.glob(currentPath + '/kaldi-scp/*.scp'):
    sys.stderr.write('[INFO %s] %s\n' % (now, scp))
    collectScp.append(scp.split('kaldi-scp/')[1].split('-wav')[0])

    f = open(scp, 'r')
    for line in f.readlines():

        input_path = line.split('-p')[1].replace('|', '').strip()
        sph_file_name = input_path.split('/')[-1]
        output_path = dest_path + '/' + sph_file_name.split('.sph')[0] + '.wav'

        with open(final_script, "a") as sh:
            sh.write("%s %s %s\n" % (command, input_path, output_path))


# prepare combined text
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
sys.stderr.write('[INFO %s] start combining tedlium audio text\n' % now)
text_path = currentPath + "/kaldi/egs/tedlium/s5_r3/data/%s/text"
for i in collectScp:
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sys.stderr.write('[INFO %s] processing %s text\n' % (now, i))
    f = open(text_path % i, 'r')
    data = f.read()

    with open(currentPath + "/text", "a") as t:
        t.write(data + '\n')


# convert sph to wav parallelly 
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
sys.stderr.write('[INFO %s] start converting sph to wav parallelly\n' % now)
def run_sh(sh_command):
    os.system(sh_command)
    pbar.update(1)

scp = open(final_script, 'r')
commandList = scp.read().split('\n')
pbar = tqdm(total=len(commandList))

pool = Pool()
pool.imap_unordered(run_sh, commandList)
pool.close()
pool.join()
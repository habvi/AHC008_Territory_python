import subprocess

for i in range(100):
    file_num = "{:04d}".format(i)

    command = ['mv',
               'in/' + file_num + '.txt',
               'in/' + str(i) + '.txt']

    subprocess.run(command)
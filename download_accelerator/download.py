import argparse
import os
import requests
import threading
import time
# from time import clock,time

''' Downloader for a set of files '''
class Downloader:
    def __init__(self):
        ''' initialize the file where the list of URLs is listed, and the
        directory where the downloads will be stored'''
        self.args = None
        self.dir = 'downloads'
        self.num_thread = 1
        self.parse_arguments()

    def parse_arguments(self):
        ''' parse arguments, which include '-i' for input file and
        '-d' for download directory'''
        parser = argparse.ArgumentParser(prog='Mass downloader', description='A simple script that downloads multiple files from a list of URLs specified in a file', add_help=True)
        parser.add_argument('-d', '--dir', type=str, action='store', help='Specify the directory where downloads are stored, default is downloads',default='downloads')
        parser.add_argument('-n', '--num_thread', type=int, action='store', help='Specify the number of thread you want to create', default=1)
        parser.add_argument('url', type=str, action='store', help='Specify the URL')
        args = parser.parse_args()
        self.dir = args.dir
        self.num_thread = args.num_thread
        self.url=args.url.strip()
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def download(self):
        r = requests.head(self.url, headers={'Accept-Encoding': 'identity'})
        # print r.headers
        content_length = int(r.headers['content-length'])
        threads = []
        thread_range = content_length / self.num_thread + 1
        start = 0
        end = start + thread_range - 1
        start_time = time.clock()
        for i in range(0,self.num_thread - 1):
            # print header
            d = DownThread(i,self.url, str(start)+'-'+str(end))
            threads.append(d)
            start = end + 1
            end += thread_range
        # print header
        threads.append(DownThread(self.num_thread - 1,self.url, str(start)+'-'+str(content_length-1)))

        for t in threads:
            t.start()
        content = ''
        for t in threads:
            content += t.join()
        end_time = time.clock()
        # print content
        with open(self.dir+'/'+self.url.split('/')[-1].strip(), 'wb') as f:
            f.write(content)
        print '%s %s %s %s' % (self.url,self.num_thread,content_length,end_time-start_time)


''' Use a thread to download one file given by url and stored in filename'''
class DownThread(threading.Thread):
    def __init__(self,i,url, byte_range):
        self.id = i
        self.url = url
        threading.Thread.__init__(self)
        self.range = byte_range
        self.content = ''

    def run(self):
        r = requests.get(self.url, headers= {'Range': 'bytes='+self.range, 'Accept-Encoding': 'identity'})
        self.content = str(r.content)

    def join(self):
        threading.Thread.join(self)
        return self.content

if __name__ == '__main__':
    d = Downloader()
    d.download()

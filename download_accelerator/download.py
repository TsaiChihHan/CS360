import argparse
import os
import requests
import threading

''' Downloader for a set of files '''
class Downloader:
    def __init__(self):
        ''' initialize the file where the list of URLs is listed, and the
        directory where the downloads will be stored'''
        self.args = None
        # self.in_file = 'urls.txt'
        self.dir = 'downloads'
        self.num_thread = 1
        self.parse_arguments()

    def parse_arguments(self):
        ''' parse arguments, which include '-i' for input file and
        '-d' for download directory'''
        parser = argparse.ArgumentParser(prog='Mass downloader', description='A simple script that downloads multiple files from a list of URLs specified in a file', add_help=True)
        # parser.add_argument('-i', '--input', type=str, action='store', help='Specify the input file containing a list of URLs, default is urls.txt',default='urls.txt')
        parser.add_argument('-d', '--dir', type=str, action='store', help='Specify the directory where downloads are stored, default is downloads',default='downloads')
        parser.add_argument('-n', '--num_thread', type=int, action='store', help='Specify the number of thread you want to create', default=1)
        parser.add_argument('url', type=str, action='store', help='Specify the URL')
        args = parser.parse_args()
        # self.in_file = args.input
        self.dir = args.dir
        self.num_thread = args.num_thread
        self.url=args.url.strip()
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)

    def download(self):
        r = requests.head(self.url)
        content_length = int(r.headers['content-length'])
        print 'content_length: ' + str(content_length)
        threads = []
        thread_range = content_length / self.num_thread
        start = 0
        end = start + thread_range - 1
        for i in range(0,self.num_thread - 1):
            header = {'Range': str(start)+'-'+str(end)}
            print header
            d = DownThread(i,self.url)
            threads.append(d)
            start = end + 1
            end += thread_range
        header = {'Range': str(start)+'-'+str(content_length-1)}
        print header
        threads.append(DownThread(self.num_thread - 1,self.url))
        # for t in threads:
        #     t.start()
        # for t in threads:
        #     t.join()

        # ''' download the files listed in the input file '''
        # # setup URLs
        # urls = []
        # f = open(self.in_file,'r')
        # for line in f.readlines():
        #     urls.append(line.strip())
        # f.close()
        # # setup download locations
        # files = [url.split('/')[-1].strip() for url in urls]
        # # create a thread for each url
        # threads = []
        # for f,url in zip(files,urls):
        #     filename = self.dir + '/' + f
        #     d = DownThread(url,filename)
        #     threads.append(d)
        # for t in threads:
        #     t.start()
        # for t in threads:
        #     t.join()

''' Use a thread to download one file given by url and stored in filename'''
class DownThread(threading.Thread):
    def __init__(self,i,url):
        self.id = i
        print 'Thread ' + str(self.id + 1)
        self.url = url
        threading.Thread.__init__(self)
        self._content_consumed = False

    def run(self):
        print 'Downloading %s' % self.url
        r = requests.get(self.url, stream=True)
        with open(self.filename, 'wb') as f:
            f.write(r.content)

if __name__ == '__main__':
    d = Downloader()
    d.download()

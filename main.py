from datetime import datetime
from pathlib import Path
from multiprocessing.dummy import Pool as ThreadPool

from googe_driver import GoogleDriver
from file_handler import FileHandler

def _file_upload(file_hndlr):
    year_id = g_driver.find_subfolder_id(pictures_id, file_hndlr.year)
    month_id = g_driver.find_subfolder_id(year_id, file_hndlr.month)
    file_id = g_driver.upload_file(file_hndlr, month_id)
    file_hndlr.cleanup()
    return file_id

def file_upload(src_file_list):
    for src_file in src_file_list:
        file_hndlr = FileHandler(src_file)
        file_id = _file_upload(file_hndlr)
        line = f'{file_id},{src_file.name},completed\n'
        log_file_fs.write(line)

def list_split(l, split_size):
    whole = len(l) // split_size
    r = len(l) % split_size
    split_inds = [(i * split_size, (i + 1) * split_size) for i in range(whole)]
    if r:
        split_inds.append((whole * split_size, whole * split_size + r))
    split_l = [l[s:e] for s,e in split_inds]
    return split_l

def read_completed(log_file_fs):
    completed = []
    if log_file.exists():
        lines = log_file_fs.readlines()
        completed = [l.split(',')[1] for l in lines[1:]]

    return completed

if __name__ == '__main__':
    project_root = Path(__file__).joinpath('..').resolve()
    log_file = project_root.joinpath('logs', f"{datetime.today().strftime('%Y%m%d')}.txt")
    if not log_file.parent.exists():
        log_file.parent.mkdir(parents=True)

    log_file_fs = open(log_file, 'r+')
    completed = read_completed(log_file_fs)

    # path to the images to be uploaded
    files = list(project_root.joinpath('my_unprocessed').resolve().glob('**/*.*'))

    files = [f for f in files if f.name not in completed]

    #path to settings file
    settings_file = project_root.joinpath('settings', 'settings.yaml')

    # instantiate a driver to handle all the actual uploading
    g_driver = GoogleDriver(settings_file)

    # google operates on objects using their id, not their name, this is the top level directory for photo storage
    pictures_id = g_driver.driver.auth.settings['photo_store_root']

    # we are going to upload in parallel, we need to create all the directories before that happens,
    #  otherwise there will be duplicates directories, again because id is disntinct not name
    distinct_dates = set(FileHandler.get_capture_date(f) for f in files)

    for year, month in distinct_dates:
        year_id = g_driver.mk_google_dir(pictures_id, year)
        month_id = g_driver.mk_google_dir(year_id, month)


    workers = 2  # Setting this higher will trip Google's rate limit
    files_per_worker = 50

    worker_file_chunks = list_split(files, files_per_worker)
    # %% Distribute tasks to workers
    pool = ThreadPool(workers) # Make the Pool of workers
    pool.map(file_upload, worker_file_chunks)
    pool.close() # close the pool and wait for the work to finish
    pool.join()

    log_file_fs.close()


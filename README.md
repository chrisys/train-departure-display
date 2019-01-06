# UK train departure screen

> Python script to display replica real-time (coming soon) UK railway station departure screens for SSD13xx devices

## Sample output

![Example output of the script](capture.png)

## Usage

1. Clone this repo

2. Install dependcies

```bash
$ pip install -r requirements.txt
```

3. Run the script

```bash
$ python ./src/main.py --display capture --width 256 --height 64
```

Change the `--display` flag to alter the output mechanism

## Thanks

The fonts used were painstakingly put together by `DanielHartUK` and can be found on GitHub at https://github.com/DanielHartUK/Dot-Matrix-Typeface - A huge thanks for making that resource available!

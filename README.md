# Architecture Diagram
![Architecture_Diagram_Assignment-4](https://user-images.githubusercontent.com/91744801/229030775-b0c05be1-c479-4f11-b11a-d33c90c612dc.png)
# Local System Setup

## For Windows Users

### Step 1: Download FFmpeg

1. Go to the [official FFmpeg website](https://ffmpeg.org/download.html#build-windows).
2. Download the latest build of FFmpeg for Windows.
3. Extract the downloaded file to a directory of your choice.

### Step 2: Add FFmpeg to System Path

1. Search for "Environment Variables" in the Windows search bar and click on "Edit the system environment variables".
2. In the System Properties window, click on the "Environment Variables" button.
3. In the "System Variables" section, scroll down and find the "Path" variable, then click on the "Edit" button.
4. Click on the "New" button and add the path to the FFmpeg bin directory (the directory where `ffmpeg.exe` is located).
5. Click "OK" to close all windows and apply the changes.

### Step 3: Verify FFmpeg Installation

1. Open a Command Prompt window.
2. Type `ffmpeg -version` and press Enter.
3. If FFmpeg is installed correctly, you should see the version information printed to the screen.

## For Mac Users

### Step 1: Install Homebrew

1. Open the Terminal app on your Mac.
2. Install Homebrew by running the following command:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```


### Step 2: Install FFmpeg

1. Open the Terminal app on your Mac.
2. Install FFmpeg by running the following command:

```sh
brew install ffmpeg
```


### Step 3: Verify FFmpeg Installation

1. Open the Terminal app on your Mac.
2. Type `ffmpeg -version` and press Enter.
3. If FFmpeg is installed correctly, you should see the version information printed to the screen.

Once you have installed FFmpeg and added it to your system path (for Windows users), you should be able to run your Streamlit application without encountering the `FileNotFoundError: [Errno 2] No such file or directory: 'ffprobe'` error.



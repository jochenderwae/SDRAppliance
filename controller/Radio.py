from distutils.version import StrictVersion

from gnuradio import audio
from gnuradio import blocks
from gnuradio import gr
from gnuradio.fft import logpwrfft
import osmosdr
import numpy

class FFTDataSink(gr.sync_block):
    def __init__(self, fftBinSize, rfSampleRate):
        gr.sync_block.__init__(
            self,
            name = "Vector sink",
            in_sig = [(numpy.float32, fftBinSize)],
            out_sig = None,
        );

        self.fftBinSize = fftBinSize;
        self.windowMin = 0;
        self.windowMax = 1;
        self.zoom = None;
        self.rfSampleRate = rfSampleRate;
        self.offsetFrequency = 0;
        self.listeners = [];

    def addListener(self, listener) :
        self.listeners.append(listener);


    def setZoom(self,zoom):
        zoom = max(0, min(zoom, .499)); # clip z to [0, 0.499]
        self.windowMin = zoom;
        self.windowMax = 1 - zoom;
        self.zoom = zoom;
        return zoom;

    def work(self, input_items, output_items):
        data = numpy.fft.fftshift(input_items);
        inputData = data[0][0].tolist();

        inputSize = len(inputData);
        outputData = [];
        windowMin = self.windowMin;
        windowMax = self.windowMax;

        # shift displayed spectrum by offset frequency
        if self.zoom != None and self.zoom > 0 and self.rfSampleRate != 0:
            df = float(self.offsetFrequency) / self.rfSampleRate;
            windowMin -= df;
            windowMax -= df;
            windowMin = max(windowMin,0);
            windowMax = min(windowMax,1);

        datasetLowerBound = int(windowMin * inputSize);
        datasetUpperBound = int(windowMax * inputSize);
        outputSize = datasetUpperBound - datasetLowerBound;
        if(outputSize > 0):
            # select zoomed data array segment
            outputData = inputData[datasetLowerBound:datasetUpperBound];
            #v = outputData[int(outputSize/2)];
            #self.ss += (v-self.ss) * self.integ_constant;
            #self.main.signal_progress_bar.setValue(self.ss)
            #self.main.signal_progress_bar.setFormat("%.1f db" % self.ss)
            for listener in self.listeners :
                listener(outputData);
        return len(input_items)


class Radio(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.volume = 20;
        self.rfSampleRate = 2560000;
        self.audioSampleRate = 48000;
        self.gain = 20;
        self.frequency = 102e6;
        self.fftBinSize = 4096;
        self.frameRate = 10;
        self.average = 0.82675;

        ##################################################
        # Blocks
        ##################################################
        self.rtlsdrSource = osmosdr.source(
            args="numchan=" + str(1) + " " + ''
        );
        self.rtlsdrSource.set_time_unknown_pps(osmosdr.time_spec_t());
        self.rtlsdrSource.set_sample_rate(self.rfSampleRate);
        self.rtlsdrSource.set_center_freq(self.frequency, 0);
        self.rtlsdrSource.set_freq_corr(0, 0);
        self.rtlsdrSource.set_gain(self.gain, 0);
        self.rtlsdrSource.set_if_gain(20, 0);
        self.rtlsdrSource.set_bb_gain(20, 0);
        self.rtlsdrSource.set_antenna('', 0);
        self.rtlsdrSource.set_bandwidth(0, 0);


        # this is the source for the FFT display's data
        self.logpwrfft = logpwrfft.logpwrfft_c(
            sample_rate=self.rfSampleRate,
            fft_size=self.fftBinSize,
            ref_scale=2,
            frame_rate=self.frameRate,
            avg_alpha=self.average,
            average=(self.average != 1)
        )


        # this is the main FFT display
        self.fftDataSink = FFTDataSink(fftBinSize=self.fftBinSize, rfSampleRate=self.rfSampleRate);

        self.leftVolume  = blocks.multiply_const_ff(self.volume);
        self.rightVolume = blocks.multiply_const_ff(self.volume);

        self.audio = audio.sink(self.audioSampleRate, '', True);

        self.connect((self.rtlsdrSource, 0), (self.logpwrfft, 0));
        self.connect((self.logpwrfft, 0), (self.fftDataSink, 0));

        self.connect((self.leftVolume, 0), (self.audio, 0));
        self.connect((self.rightVolume, 0), (self.audio, 1));

        self.demod = None;


        ##################################################
        # Connections
        ##################################################
        #self.setDemod(self.demod);

    def setDemod(self, demod) :
        if self.demod != None:
            self.disconnect(self.demod);
        self.demod = demod;
        if self.demod != None:
            self.connect((self.rtlsdrSource, 0), (self.demod, 0));
            self.connect((self.demod, 0), (self.leftVolume, 0));
            self.connect((self.demod, 1), (self.rightVolume, 0));
            self.demod.set_rf_samp_rate(self.rfSampleRate);
            self.demod.set_audio_sample_rate(self.audioSampleRate);

    def addFFTDataListener(self, listener) :
        self.fftDataSink.addListener(listener);

    def getVolume(self):
        return self.volume;

    def set_volume(self, volume):
        self.volume = volume;
        self.leftVolume.set_k(self.volume);
        self.rightVolume.set_k(self.volume);

    def getAudioSampleRate(self):
        return self.audioSampleRate;

    def setAudioSampleRate(self, audioSampleRate):
        self.audioSampleRate = audioSampleRate;
        self.rtlsdrSource.audio_sample_rate(self.audioSampleRate);
        if self.demod != None:
            self.demod.audio_sample_rate(self.audioSampleRate);

    def getRFSampleRate(self):
        return self.rfSampleRate

    def setRFSampleRate(self, rfSampleRate):
        self.rfSampleRate = rfSampleRate;
        self.rtlsdrSource.set_sample_rate(self.rfSampleRate);
        if self.demod != None:
            self.demod.set_rf_samp_rate(self.rfSampleRate);

    def getGain(self):
        return self.gain;

    def setGain(self, gain):
        self.gain = gain;
        self.rtlsdrSource.set_gain(self.gain, 0);

    def getFrequency(self):
        return self.frequency;

    def setFrequency(self, frequency):
        self.frequency = frequency;
        self.rtlsdrSource.set_center_freq(self.frequency, 0);

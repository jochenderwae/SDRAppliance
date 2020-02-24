from distutils.version import StrictVersion

from gnuradio import audio
from gnuradio import blocks
from gnuradio import gr
import osmosdr

class Radio(gr.top_block):

    def __init__(self):

        ##################################################
        # Variables
        ##################################################
        self.volume = 20;
        self.rfSampleRate = 2048e3;
        self.audioSampleRate = 48000;
        self.gain = 20;
        self.frequency = 102 * 1000000;

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
        self.rtlsdrSource.set_gain(gain, 0);
        self.rtlsdrSource.set_if_gain(20, 0);
        self.rtlsdrSource.set_bb_gain(20, 0);
        self.rtlsdrSource.set_antenna('', 0);
        self.rtlsdrSource.set_bandwidth(0, 0);

        self.leftVolume  = blocks.multiply_const_ff(self.volume);
        self.rightVolume = blocks.multiply_const_ff(self.volume);

        self.audio = audio.sink(self.audioSampleRate, '', True);

        self.demod = None;


        ##################################################
        # Connections
        ##################################################
        self.connect((self.leftVolume, 0), (self.audio, 0));
        self.connect((self.rightVolume, 0), (self.audio, 1));
        setDemod(self.demod);

    def setDemod(demod) :
        if self.demod != None:
            self.disconnect(self.demod);
        self.demod = demod;
        if self.demod != None:
            self.connect((self.rtlsdr_source_0, 0), (self.demod, 0));
            self.connect((self.demod, 0), (self.leftVolume, 0));
            self.connect((self.demod, 1), (self.rightVolume, 0));
            self.demod.set_rf_samp_rate(self.rfsamprate);
            self.demod.audio_sample_rate(self.audioSampleRate);

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

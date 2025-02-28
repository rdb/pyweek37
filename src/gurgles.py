from panda3d.core import AudioSound


MAX_VOLUME = 0.5
FADEIN_TIME = 2.0
FADEOUT_TIME = 2.0


class MultiTrack:
    def __init__(self):
        self.mgr = base.musicManager

        self.sounds = {}
        self.playing = set()

        self.task = None

    def load_track(self, name, file):
        if name not in self.sounds:
            self.sounds[name] = loader.load_music(file)
            self.sounds[name].set_loop(False)
            self.sounds[name].set_volume(0.0)
            self.mgr.set_concurrent_sound_limit(len(self.sounds) + 1)

    def set_playing_tracks(self, tracks):
        self.playing = set(tracks)

    def play(self):
        for sound in self.sounds.values():
            sound.play()

        if not self.task:
            self.task = taskMgr.add(self.do_fade_task)

    def stop(self):
        if self.task:
            self.task.remove()
            self.task = None

        for sound in self.sounds.values():
            sound.stop()

    def do_fade(self):
        restart = False
        for name, sound in self.sounds.items():
            vol = sound.get_volume()
            if name in self.playing:
                if vol < MAX_VOLUME:
                    sound.set_volume(min(MAX_VOLUME, vol + base.clock.dt / FADEIN_TIME))
            else:
                if vol > 0.0:
                    sound.set_volume(max(0.0, vol - base.clock.dt / FADEOUT_TIME))

            if sound.status() != AudioSound.PLAYING and sound.get_time() > 10.0:
                restart = True

        if restart:
            for sound in self.sounds.values():
                sound.set_time(0.0)
                sound.play()

    def do_fade_task(self, task):
        self.do_fade()
        return task.cont

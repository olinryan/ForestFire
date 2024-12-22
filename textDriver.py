#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
from fetchHeadlines import fetch_headlines
import datetime
import time
from importSpotify import getSpotifyPlaying
import os

class RunText(SampleBase):
    def __init__(self, text, font_path="fonts/8x13.bdf", news_color=(255, 255, 0), scroll_speed=0.05, *args, **kwargs):
        """
        Initialize the RunText class with customizable inputs.
        
        :param text: The text to scroll on the matrix.
        :param font_path: Path to the font file.
        :param text_color: A tuple (R, G, B) representing text color.
        :param scroll_speed: Speed of the scrolling text (seconds per frame).
        """
        super(RunText, self).__init__(*args, **kwargs)
        self.text = text
        self.font_path = font_path
        self.news_color = news_color
        self.scroll_speed = scroll_speed

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont(self.font_path)
        font2 = graphics.Font()
        font2.LoadFont('fonts/6x9.bdf')
        font3 = graphics.Font()
        font3.LoadFont('fonts/6x10.bdf')
        NewsColor = graphics.Color(*self.news_color)
        pos = offscreen_canvas.width
        pos2 = 0
        scrollCounter = [0,0]
        playing = getSpotifyPlaying()
        playing = None
        # playingText = f'{playing["Track"]} - {playing["Artist"]}'
        inc = 0.25  # incriment for spotify track position change
        while True:
            offscreen_canvas.Clear()
            
            # Scroll the news
            text_length = graphics.DrawText(offscreen_canvas, font, pos, 9, NewsColor, self.text)
            pos -= 1
            if pos + text_length < 0:
                pos = 0
                scrollCounter[0] += 1
                if scrollCounter[0] == 15:     # Update every 15 scrolls
                    self.text=fetch_headlines(['world','us','business','politics','arts'])
                    scrollCounter[0] = 0

            # Get the time
            currentDT = time.strftime("%a %b %d")
            currentDT2= time.strftime("%I:%M:%S")
            graphics.DrawText(offscreen_canvas, font2, 0, 25, graphics.Color(180,255,70), currentDT)
            graphics.DrawText(offscreen_canvas, font2, 0, 32, graphics.Color(180,255,70), currentDT2)
            
            # Scroll spotify track
            if playing != None:
                text_length2 = graphics.DrawText(offscreen_canvas, font3, pos2, 17, graphics.Color(80,0,255), playingText)
                pos2 -= inc
                if pos2 + text_length2 < offscreen_canvas.width:
                    inc = inc*-1
                    scrollCounter [1]+= 1
                if pos2  > 0:
                    inc = inc*-1
                    scrollCounter [1]+= 1
                if scrollCounter[1] == 6:     # Update every 2 scrolls
                    playing = getSpotifyPlaying()
                    playingText = f'{playing["Track"]} - {playing["Artist"]}'
                    scrollCounter[1] = 0

            # wait
            time.sleep(self.scroll_speed)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    # Instantiate the class with your desired parameters
    run_text = RunText(
        text=fetch_headlines(['world','us','business','politics']), 
        news_color=(255, 0,0),  # Cyan text
        scroll_speed=0.03  # Faster scroll speed
    )

    if not run_text.process():
        print("Failed to initialize the RunText application.")

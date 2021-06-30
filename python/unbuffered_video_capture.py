"""
Original:
https://stackoverflow.com/questions/43665208/how-to-get-the-latest-frame-from-capture-device-camera-in-opencv
"""

import cv2, queue, threading, time, os


# bufferless VideoCapture
class UnbufferedVideoCapture:

	def __init__(self, source):
		self.cap = cv2.VideoCapture(source)
		if os.path.isfile(source):
			self.from_file = True
			self.fps = self.cap.get(cv2.CAP_PROP_FPS)
			self.interval = 1./self.fps
		else:
			self.from_file = False
		
		self.q = queue.Queue()
		t = threading.Thread(target=self._reader)
		t.daemon = True
		t.start()

	# read frames as soon as they are available, keeping only most recent one
	def _reader(self):
		while True:
			start = time.time()

			ret, frame = self.cap.read()
			if not ret:
				break
			if not self.q.empty():
				try:
					self.q.get(block = False)   # discard previous (unprocessed) frame
				except queue.Empty:
					pass
			self.q.put(frame, block = False)

			end = time.time()
			if self.from_file:
				time.sleep(max(0, self.interval - end + start))
				# time.sleep(self.interval)

	def read(self):
		return self.q.get()



def test(source, delay, imshow = False):
	cap = UnbufferedVideoCapture(source)

	start = time.time()
	while True:
		end = time.time()
		fps = 1./(end - start)
		start = end
		print('FPS:', fps)

		frame = cap.read()
		if imshow:
			cv2.imshow("frame", frame)
			if chr(cv2.waitKey(1)&255) == 'q':
				break

		time.sleep(delay)   # simulate time between events


if __name__ == '__main__':
	DELAY = 0.05  # seconds
	# SOURCE = 0
	SOURCE = '/home/dangnh/Desktop/vtcc_original.mp4'
	print('EXPECTED FPS:', 1./DELAY)
	test(SOURCE, DELAY, imshow = False)
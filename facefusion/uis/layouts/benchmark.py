import gradio

from facefusion import state_manager
from facefusion.download import conditional_download
from facefusion.uis.components import about, benchmark, benchmark_options, execution, execution_queue_count, execution_thread_count, frame_processors, frame_processors_options, memory


def pre_check() -> bool:
	if not state_manager.get_item('skip_download'):
		conditional_download('.assets/examples',
		[
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.jpg',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/source.mp3',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-240p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-360p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-540p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-720p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-1080p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-1440p.mp4',
			'https://github.com/facefusion/facefusion-assets/releases/download/examples/target-2160p.mp4'
		])
		return True
	return False


def pre_render() -> bool:
	return True


def render() -> gradio.Blocks:
	with gradio.Blocks() as layout:
		with gradio.Row():
			with gradio.Column(scale = 2):
				with gradio.Blocks():
					about.render()
				with gradio.Blocks():
					frame_processors.render()
				with gradio.Blocks():
					frame_processors_options.render()
				with gradio.Blocks():
					execution.render()
					execution_thread_count.render()
					execution_queue_count.render()
				with gradio.Blocks():
					memory.render()
				with gradio.Blocks():
					benchmark_options.render()
			with gradio.Column(scale = 5):
				with gradio.Blocks():
					benchmark.render()
	return layout


def listen() -> None:
	frame_processors.listen()
	frame_processors_options.listen()
	execution.listen()
	execution_thread_count.listen()
	execution_queue_count.listen()
	memory.listen()
	benchmark.listen()


def run(ui : gradio.Blocks) -> None:
	ui.launch(show_api = False, inbrowser = state_manager.get_item('open_browser'))

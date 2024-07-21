from typing import Optional, Tuple

import gradio

import facefusion
from facefusion import state_manager, wording
from facefusion.common_helper import get_first, get_last
from facefusion.jobs import job_manager
from facefusion.typing import UiWorkflow
from facefusion.uis.core import get_ui_component
from facefusion.uis import choices as uis_choices

UI_WORKFLOW_DROPDOWN : Optional[gradio.Dropdown] = None


def render() -> None:
	global UI_WORKFLOW_DROPDOWN

	UI_WORKFLOW_DROPDOWN = gradio.Dropdown(
		label = wording.get('uis.ui_workflow'),
		choices = facefusion.choices.ui_workflows,
		value = state_manager.get_item('ui_workflow')
	)


def listen() -> None:
	instant_runner_wrapper = get_ui_component('instant_runner_wrapper')
	job_runner_wrapper = get_ui_component('job_runner_wrapper')
	job_runner_job_action_dropdown = get_ui_component('job_runner_job_action_dropdown')
	job_runner_job_id_dropdown = get_ui_component('job_runner_job_id_dropdown')
	job_manager_wrapper = get_ui_component('job_manager_wrapper')
	job_manager_job_action_dropdown = get_ui_component('job_manager_job_action_dropdown')
	job_manager_job_id_textbox = get_ui_component('job_manager_job_id_textbox')

	if instant_runner_wrapper and job_runner_wrapper and job_runner_job_action_dropdown and job_runner_job_id_dropdown and job_manager_wrapper and job_manager_job_action_dropdown and job_manager_job_id_textbox:
		UI_WORKFLOW_DROPDOWN.change(update_ui_workflow, inputs = UI_WORKFLOW_DROPDOWN, outputs = [ instant_runner_wrapper, job_runner_wrapper, job_runner_job_action_dropdown, job_runner_job_id_dropdown, job_manager_wrapper, job_manager_job_action_dropdown, job_manager_job_id_textbox ])


def update_ui_workflow(ui_workflow : UiWorkflow) -> Tuple[gradio.Group, gradio.Group, gradio.Dropdown, gradio.Dropdown, gradio.Group, gradio.Dropdown, gradio.Textbox]:
	if ui_workflow == 'instant_runner':
		return gradio.Group(visible = True), gradio.Group(visible = False), gradio.Dropdown(), gradio.Dropdown(), gradio.Group(visible = False), gradio.Dropdown(), gradio.Textbox()
	if ui_workflow == 'job_runner':
		queued_job_ids = job_manager.find_job_ids('queued') or [ 'none' ]

		return gradio.Group(visible = False), gradio.Group(visible = True), gradio.Dropdown(value = get_first(uis_choices.job_runner_actions), choices = uis_choices.job_runner_actions), gradio.Dropdown(value = get_last(queued_job_ids), choices = queued_job_ids), gradio.Group(visible = False), gradio.Dropdown(), gradio.Textbox()
	if ui_workflow == 'job_manager':
		return gradio.Group(visible = False), gradio.Group(visible = False), gradio.Dropdown(), gradio.Dropdown(), gradio.Group(visible = True), gradio.Dropdown(value = get_first(uis_choices.job_manager_actions)), gradio.Textbox(value = None)
	return gradio.Group(), gradio.Group(), gradio.Dropdown(), gradio.Dropdown(), gradio.Group(), gradio.Dropdown(), gradio.Textbox()

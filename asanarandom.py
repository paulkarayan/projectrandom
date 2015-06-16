
from utils import asana_utils as asana
from utils.asana_utils import AsanaException
import gevent
from gevent import monkey

ASANA_API_KEY = None
MAX_GREENLETS = 10

def main():
    monkey.patch_all()

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project_list', default=None, required=False)
    parser.add_argument('-n', '--num_tasks', default=1, required=False)
    parser.add_argument('-k', '--asana_api_key', default=ASANA_API_KEY)
    parser.add_argument('-w', '--workspace', default=None, required=False)
    args = parser.parse_args()

    asana_api = asana.AsanaAPI(debug=True)

    # collect tasks from project
    universal_result_list = list()
    if project_list == None:
        project_list = [project['id'] for project in asana_api.list_projects(include_archived=False)]
    else:
        pass

    pool = Pool(MAX_GREENLETS)
    [pool.spawn(get_asana_project, asana_api, project_id, num_projects) for project_id in project_list]
    pool.join()

    # select task, url at random from each project
    # remove the parent map rows first!
    selected_tasks = []    

    # email tasks 


def get_asana_project(asana_api, project_id, universal_result_list):

    result = fetch_project(asana_api, project_id)
    if result:
        project, firm_id = result

        result = get_asana_tasks(asana_api, project_id)
        if result:
            tasks, parent_map, project_map, comments, tags, task_properties = result
            universal_result_list.append(result)
    return



def get_asana_tasks(asana_api, project_id):

    # Fetch list of tasks
    try:
        tasks = asana_api.get_project_tasks(project_id)
    except AsanaException as e:
        print e.message
        print 'Failed to request tasks for project id {}.'.format(project_id)
        return None

    task_rows = []
    task_property_rows = []
    parent_map_rows = []
    project_map_rows = []
    comment_rows = []
    tag_rows = []
    sequence = 0

    for task_obj in tasks:

        # Fetch task by id
        task_id = task_obj['id']
        project_map_rows.append([task_id, project_id])
        result = fetch_task(asana_api, project_id, task_id)
        if result:
            task_row, parent_map_row, section = result
            task_rows.append(task_row)
            if parent_map_row:
                parent_map_rows.append(parent_map_row)

            # Fetch comments by task id
            result = fetch_comments(asana_api, task_id)
            if result:
                comment_rows += result

            # Fetch tags by task id
            result = fetch_tags(asana_api, task_id)
            if result:
                tag_rows += result

            # Collect task section and order
            sequence += 1
            task_property_rows.append([project_id, task_id, section, sequence])

    return task_rows, parent_map_rows, project_map_rows, comment_rows, tag_rows, task_property_rows

def fetch_task(asana_api, project_id, task_id):
    try:
        task = asana_api.get_task(task_id)
    except AsanaException as e:
        print e.message
        print 'Failed to request task id {}.'.format(task_id)
        return None

    task_row = [task_id, task['name'], task['assignee']['name'] if task['assignee'] else None,
                arrow.get(task['created_at']).format(SQL_DATETIME_FORMAT),
                arrow.get(task['modified_at']).format(SQL_DATETIME_FORMAT), task['notes'],
                1 if task['completed'] else 0,
                arrow.get(task['completed_at']).format(SQL_DATETIME_FORMAT) if task['completed'] else None,
                date_run]

    if task['parent']:
        parent_map_row = [task_id, task['parent']['id']]
    else:
        parent_map_row = None

    section = None
    for membership in task['memberships']:
        if membership['project']['id'] == project_id:
            if membership['section']:
                section = membership['section']['name']

    return task_row, parent_map_row, section




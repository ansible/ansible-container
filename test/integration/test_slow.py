import os
import pytest

from scripttest import TestFileEnvironment as ScriptTestEnvironment  # rename to avoid pytest collect warning


def project_dir(name):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(test_dir, 'projects', name)


@pytest.mark.timeout(240)
def test_build_minimal_docker_container():
    env = ScriptTestEnvironment()
    result = env.run('ansible-container', 'build', '--flatten', cwd=project_dir('minimal'), expect_stderr=True)
    assert "Aborting on container exit" in result.stdout
    assert "Exported minimal-minimal with image ID " in result.stderr


def test_run_minimal_docker_container():
    env = ScriptTestEnvironment()
    result = env.run('ansible-container', 'run', cwd=project_dir('minimal'), expect_stderr=True)
    assert "ansible_minimal_1 exited with code 0" in result.stdout


def test_run_minimal_docker_container_in_detached_mode():
    env = ScriptTestEnvironment()
    result = env.run('ansible-container', 'run', '--detached', cwd=project_dir('minimal'), expect_stderr=True)
    assert "Deploying application in detached mode" in result.stderr


@pytest.mark.timeout(240)
def test_stop_minimal_docker_container():
    env = ScriptTestEnvironment()
    env.run('ansible-container', 'build', '--flatten',
            cwd=project_dir('minimal_sleep'), expect_stderr=True)
    env.run('ansible-container', 'run', '--detached', cwd=project_dir('minimal_sleep'), expect_stderr=True)
    result = env.run('ansible-container', 'stop', cwd=project_dir('minimal_sleep'), expect_stderr=True)
    assert "Stopping ansible_minimal1_1 ... done" in result.stderr
    assert "Stopping ansible_minimal2_1 ... done" in result.stderr


def test_stop_service_minimal_docker_container():
    env = ScriptTestEnvironment()
    env.run('ansible-container', 'run', '--detached', cwd=project_dir('minimal_sleep'), expect_stderr=True)
    result = env.run('ansible-container', 'stop', 'minimal1',
                     cwd=project_dir('minimal_sleep'), expect_stderr=True)
    assert "Stopping ansible_minimal1_1 ... done" in result.stderr
    assert "Stopping ansible_minimal2_1 ... done" not in result.stderr


#def test_shipit_minimal_docker_container():
#    env = ScriptTestEnvironment()
#    result = env.run('ansible-container', 'shipit', 'kube', cwd=project_dir('minimal'), expect_error=True)
#    assert result.returncode == 1
#    assert "Role minimal created" in result.stderr

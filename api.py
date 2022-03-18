import connexion
from flask import Response, json
import yaml
import subprocess
import uuid
import shutil
from pathlib import Path

TMPDIR = "/tmp/stress-api-jobs"


class StressNG:

    @staticmethod
    def run_inline(sng_args):
        sng_fullpath = shutil.which("stress-ng")
        result = subprocess.run(
            [sng_fullpath] + sng_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return {"retcode": result.returncode, "info": result.stdout.decode()}

    @staticmethod
    def run_job(sng_job: str):
        job_id = str(uuid.uuid4())[:8]
        job_path = f'{TMPDIR}/{job_id}.job'
        result_path = f'{TMPDIR}/{job_id}.result'
        try:
            Path(TMPDIR).mkdir(exist_ok=True)
            with open(job_path, 'w') as f:
                f.write(sng_job)
            res = StressNG.run_inline(
                ["--quiet", "--yaml", result_path, "--job", job_path])

            if res["retcode"] == 0:
                with open(result_path, 'r') as f:
                    yaml_result = yaml.safe_load(f)
                res["info"] = yaml_result
            return res
        except:
            raise
        finally:
            Path(job_path).unlink(missing_ok=True)
            Path(result_path).unlink(missing_ok=True)


def _response(result):
    return Response(response=json.dumps(result),
                    mimetype="application/json",
                    status=200 if result["retcode"] == 0 else 503)


def liveness():
    return "iamok"


def readiness():
    result = StressNG.run_inline(
        ["--vm", "1", "--vm-bytes", "4K", "--vm-ops", "1", "--timeout", "1s"])
    return _response(result)


def runjob(jobfile):
    result = StressNG.run_job(str(jobfile, "utf-8"))
    return _response(result)


if __name__ == '__main__':
    app = connexion.FlaskApp(__name__, port=8080)
    app.add_api('openapi.yaml', arguments={'title': 'Stress-ng REST API'})
    app.run()

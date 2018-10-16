"Utility functions to help deal with user environment"
from ..imports.torch import *
from ..core import *

__all__ = ['show_install']

def show_install(show_nvidia_smi:bool=False):
    "Print user's setup information: python -c 'import fastai; fastai.show_install()'"

    import platform, fastai.version, subprocess

    rep = []
    rep.append(["platform", platform.platform()])

    opt_mods = []

    if platform.system() == 'Linux':
        try:
            import distro
        except ImportError:
            opt_mods.append('distro');
            # partial distro info
            rep.append(["distro", platform.uname().version])
        else:
            # full distro info
            rep.append(["distro", ' '.join(distro.linux_distribution())])

    cenv = 'CONDA_DEFAULT_ENV'
    rep.append(["conda env", (os.environ[cenv] if (cenv in os.environ and len(os.environ[cenv])) else "Unknown")])

    rep.append(["python version", platform.python_version()])
    rep.append(["fastai version", fastai.__version__])
    rep.append(["torch version",  torch.__version__])

    # nvidia-smi
    cmd = "nvidia-smi"
    have_nvidia_smi = False
    try:
        result = subprocess.run(cmd.split(), shell=False, check=False, stdout=subprocess.PIPE)
    except:
        pass
    else:
        if result.returncode == 0 and result.stdout:
            have_nvidia_smi = True

    # XXX: if nvidia-smi is not available, another check could be:
    # /proc/driver/nvidia/version on most systems, since it's the
    # currently active version

    if have_nvidia_smi:
        smi = result.stdout.decode('utf-8')
        # matching: "Driver Version: 396.44"
        match = re.findall(r'Driver Version: +(\d+\.\d+)', smi)
        if match: rep.append(["nvidia driver", match[0]])

    rep.append(["torch cuda is",
                f"{'' if torch.cuda.is_available() else 'Not '}available"])
    rep.append(["torch cuda ver", torch.version.cuda])

    # disable this info for now, seems to be available even on cpu-only systems
    #rep.append(["cudnn", torch.backends.cudnn.version()])
    #rep.append(["cudnn avail", torch.backends.cudnn.enabled])

    gpu_cnt = torch.cuda.device_count()
    rep.append(["torch gpus", gpu_cnt])

    # it's possible that torch might not see what nvidia-smi sees?
    gpu_total_mem = []
    if have_nvidia_smi:
        try:
            cmd = "nvidia-smi --query-gpu=memory.total --format=csv,nounits,noheader"
            result = subprocess.run(cmd.split(), shell=False, check=False, stdout=subprocess.PIPE)
        except:
            print("have nvidia-smi, but failed to query it")
        else:
            if result.returncode == 0 and result.stdout:
                output = result.stdout.decode('utf-8')
                gpu_total_mem = [int(x) for x in output.strip().split('\n')]

    # information for each gpu
    for i in range(gpu_cnt):
        rep.append([f"  [gpu{i}]", None])
        rep.append(["  name", torch.cuda.get_device_name(i)])
        if gpu_total_mem: rep.append(["  total mem", f"{gpu_total_mem[i]}MB"])

    print("\n\n```")

    keylen = max([len(e[0]) for e in rep])
    for e in rep:
        print(f"{e[0]:{keylen}}", (f": {e[1]}" if e[1] is not None else ""))

    if have_nvidia_smi:
        if show_nvidia_smi == True: print(f"\n{smi}")
    else:
        if gpu_cnt:
            # have gpu, but no nvidia-smi
            print("no nvidia-smi is found")
        else:
            print("no supported gpus found on this system")

    print("```\n")

    print("Please make sure to include opening/closing ``` when you paste into forums/github to make the reports appear formatted as code sections.\n")

    if opt_mods:
        print("Optional package(s) to enhance the diagnostics can be installed with:")
        print(f"pip install {' '.join(opt_mods)}")
        print("Once installed, re-run this utility to get the additional information")

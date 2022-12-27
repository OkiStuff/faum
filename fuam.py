import typing as t
import typer
import json
import git
import sys
import os
import pathlib
import subprocess

fuam_path: pathlib.Path = pathlib.Path(os.path.dirname(os.path.abspath(sys.argv[0])))
cli: typer.Typer = typer.Typer()

@cli.command()
def configure() -> None:
    print("fuam configure 0.1\n")
    evaluate_response = lambda x, d: True if (x == "yes" or x == "y") else (d if x == "" else False)
    
    configuration: t.Dict[str, t.Union[str, bool, None]] = {
        "flipperzero-firmware-dir": None,
        "auto-build": None,
        "auto-upload": None
    }
    
    if (evaluate_response(input("Do you have the Flipper Zero firmware downloaded? [y/N] "), False)):
        configuration["flipperzero-firmware-dir"] = str(pathlib.Path(input("Path to the Flipper Zero firmware: ")))
    elif (evaluate_response(input("Do you want to download the Flipper Zero Firmware? [Y/n] "), True)):
        configuration["flipperzero-firmware-dir"] = f"{pathlib.Path(f'{fuam_path}/firmware')}"
        print("Downloading flipperdevices@flipperzero-firmware from github...")
        git.Repo.clone_from("https://github.com/flipperdevices/flipperzero-firmware/", configuration["flipperzero-firmware-dir"], None, None, ["--recursive"])
    else:
        print("Re-run `fuam configure` after you downloaded the Flipper Zero firmware")
        exit(0)
    
    configuration["auto-build"] = evaluate_response(input("Do you want fuam to build the application after download? [Y/n] "), True)
    
    if (configuration["auto-build"]):
        configuration["auto-upload"] = evaluate_response(input("Do you want fuam to upload the application after being built [Y/n] "), True)
    
    with open(str(pathlib.Path(f'{fuam_path}/configuration.fuam')), "w") as f:
        json.dump(configuration, f, indent=4)
        print(f"Saved configuration file to {pathlib.Path(f'{fuam_path}/configuration.fuam')}")

@cli.command()
def get(link: str, app_id: str, dist_name: t.Optional[t.Union[str, None]] = None) -> None:
    print("fuam get 0.1\n")
    dist: str = dist_name if dist_name != None else pathlib.Path(link).name # Funky solution, but this will return the last part of the URL
    
    with open(str(pathlib.Path(f"{faum_path}/configuration.fuam"))) as f:
        configuration: t.Dict[str, t.Union[str, bool, None]] = json.load(f)
        
    dist_path: pathlib.Path = pathlib.Path(f"{configuration['flipperzero-firmware-dir']}/applications_user/{dist}")
    print(f"Downloading {link} to {dist_path}...")
    git.Repo.clone_from(link, dist_path, None, None, ["--recursive"])
    
    if (configuration["auto-build"]):
        os.chdir(configuration["flipperzero-firmware-dir"])
        subprocess.run([str(pathlib.Path("./fbt")), f"fbt_{app_id}"])
        
        if (configuration["auto-upload"]):
            subprocess.run([str(pathlib.Path("./fbt")), "launch_app", f"APPSRC='{pathlib.Path(f'./applications_user/{dist}')}"])

@cli.command()
def version() -> None:
    print("Flipper User Application Manager 0.1")

if __name__ == "__main__":
    cli()
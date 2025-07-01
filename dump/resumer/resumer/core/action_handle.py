import shutil
import tempfile
import typing
from resumer.core.cfgs import RuntimeConfig
import os
from resumer.utils import check_matches, copy_file_wc, extract_inbetween_p, is_program_installed

class ActionHandler:
    def __init__(self, config : RuntimeConfig = None):
        if config is None:
            config = {}
        self.__rtconfig : RuntimeConfig | dict = config
        self.__tempfolder = tempfile.TemporaryDirectory()

    def post_handler(self):
        self.__tempfolder.cleanup()
    
    def pre_process(self):
        if not is_program_installed("pandoc"):
            raise Exception("pandoc not installed")

    def post_process(self):
        if self.__rtconfig.get("bkup_temp_dir", False):
            shutil.copytree(
                self.__tempfolder.name,
                self.__rtconfig.bkup_temp_dir
            )

        self.__tempfolder.cleanup()

    def _handle(self, action : dict, remainderConfig : dict):
        type_ = action.get("type")
        if not hasattr(self, f"handle_{type_}"):
            raise Exception(f"Unknown action type: {type_}")
        getattr(self, f"handle_{type_}")(**action, **remainderConfig)

    def __formatter(self, k, v, actionDict : dict | list, ctx : dict):
        if "$preset$" in v:
            actionDict[k] = v.replace("$preset$", ctx["template_dir"])
        if "$cache$" in v:
            actionDict[k] = v.replace("$cache$", ctx["cache_dir"])
        if "$shared$" in v:
            actionDict[k] = v.replace("$shared$", ctx["shared_dir"])

        # if there are 2 or more % in the string
        if "%" in v and v.count("%") > 1:
            res= extract_inbetween_p(v)
            for r, df in res.items():
                if r in self.__rtconfig:
                    actionDict[k] = actionDict[k].replace(f"%{r}%", str(self.__rtconfig[r]))
                else:
                    actionDict[k] = actionDict[k].replace(f"%{r}%", str(df))


    def __parse_tags(self, struct : dict | list, ctx : dict):
        if isinstance(struct, list):
            for i, d in enumerate(struct):
                if isinstance(d, dict):
                    self.__parse_tags(d, ctx)
                else:
                    self.__formatter(i, d, struct, ctx)
            return
        for k, v in struct.items():
            if isinstance(v, str):
                self.__formatter(k, v, struct, ctx)
            
            elif isinstance(v, list):
                self.__parse_tags(v, ctx)

            elif isinstance(v, dict):
                self.__parse_tags(v, ctx)

            
    def generate(self, actionDict : dict, ctx : dict):
        self.pre_process()

        bkup_cwd = os.getcwd()
        os.chdir(self.__tempfolder.name)

        self.__parse_tags(actionDict, ctx)

        actionsRaw = actionDict.pop("action", [])
        for action in actionsRaw:
            self._handle(action, actionDict)

        os.chdir(bkup_cwd)

        if self.__rtconfig.get("debug", False):
            self.handle_open_temp(**actionDict)
            input("Press Enter to continue...")

        self.copyback(**actionDict)

        self.post_process()

    # handles
    def handle_check_installed(self, name : str, **kwargs):
        if not is_program_installed(name):
            raise Exception(f"{name} not installed")
        
    def handle_ensure_cache(self, **kwargs):
        pass

    def handle_run_pandoc(
        self, 
        output : str, 
        template : str = None,
        outputType : str = None,
        **kwargs
    ):
        
        command = f'pandoc input.md -o "{output}" -f markdown -t {outputType}'
        if template is not None:
            command += f' --template="{template}"'

        os.system(command)

    def handle_run_xelatex(
        self,
        input : str,
        includeDirs : typing.List[str] = [],
        **kwargs
    ):
        if not is_program_installed("xelatex"):
            raise RuntimeError("xelatex is not installed")

        cmd = f'xelatex {input} \
-output-directory="{self.__tempfolder.name}" \
-jobname="{os.path.basename(input).replace(".tex", "")}"'

        if len(includeDirs) > 0:
            for d in includeDirs:
                cmd += f' -include-directory="{d}"'

        os.system(cmd)
    
    def handle_open_temp(self, **kwargs):
        os.startfile(self.__tempfolder.name)

    def copyback(
        self, 
        copyback_includes : typing.List[str] = [],
        copyback_excludes : typing.List[str] = [],
        **kwargs
    ):
        if len(copyback_includes) == 0 and len(copyback_excludes) == 0:
            # find the file thats last modified
            last_modified = 0
            last_path = None
            for file in os.listdir(self.__tempfolder.name):
                if file.endswith("log"):
                    if self.__rtconfig.get("copyback_log", False):
                        copy_file_wc(
                            os.path.join(self.__tempfolder.name, file),
                            os.path.join(os.getcwd(), file)
                        )
                    continue

                file_path = os.path.join(self.__tempfolder.name, file)
                if os.path.isfile(file_path):
                    if os.path.getmtime(file_path) > last_modified:
                        last_modified = os.path.getmtime(file_path)
                        last_path = file_path

            if last_path is None:
                raise Exception("No files found")
            
            copy_file_wc(
                last_path,
                os.path.join(os.getcwd(), os.path.basename(last_path))
            )
            return

        for file in os.listdir(self.__tempfolder.name):
            # check if name matches pattern
            if check_matches(file, copyback_includes) and not check_matches(file, copyback_excludes):
                copy_file_wc(
                    os.path.join(self.__tempfolder.name, file),
                    os.path.join(os.getcwd(), file)
                )
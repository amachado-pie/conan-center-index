from conan import ConanFile
from conan.tools.files import get, replace_in_file, copy, export_conandata_patches, apply_conandata_patches
from conan.tools.layout import basic_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=2.1.0"


class CcclConan(ConanFile):
    name = "cccl"
    description = "Unix cc compiler to Microsoft's cl compiler wrapper"
    topics = ("msvc", "visual studio", "wrapper", "gcc")
    homepage = "https://github.com/swig/cccl/"
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"
    options = {
        "muffle": [True, False],
        "verbose": [True, False],
    }
    default_options = {
        "muffle": True,
        "verbose": False,
    }

    @property
    def _cccl_dir(self):
        return os.path.join(self.package_folder, "bin")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if not is_msvc(self):
            raise ConanInvalidConfiguration("This recipe only supports msvc/Visual Studio.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def build(self):
        cccl_path = os.path.join(self.source_folder, self.source_folder, "cccl")
        replace_in_file(self, cccl_path,
                              "    --help)",
                              "    *.lib)\n"
                              "        linkopt+=(\"$lib\")"
                              "        ;;\n\n"
                              "    --help)")
        replace_in_file(self, cccl_path,
                              "clopt+=(\"$lib\")",
                              "linkopt+=(\"$lib\")")
        replace_in_file(self, cccl_path,
                              "    -L*)",
                              "    -LIBPATH:*)\n"
                              "        linkopt+=(\"$1\")\n"
                              "        ;;\n\n"
                              "    -L*)")

    def package(self):
        copy(self, pattern="cccl", src=os.path.join(self.source_folder, self.source_folder), dst=self._cccl_dir)
        copy(self, pattern="COPYING", src=os.path.join(self.source_folder, self.source_folder), dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        cccl_args = [
            "sh",
            os.path.join(self.package_folder, "bin", "cccl"),
        ]
        if self.options.muffle:
            cccl_args.append("--cccl-muffle")
        if self.options.verbose:
            cccl_args.append("--cccl-verbose")
        cccl = " ".join(cccl_args)

        self.buildenv_info.define("CC", cccl)
        self.buildenv_info.define("CXX", cccl)
        self.buildenv_info.define("LD", cccl)

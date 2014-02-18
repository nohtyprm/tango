
# the Tango frontend

import argparse
import sys

from tangolib.parser import Parser
from tangolib.processor import DocumentProcessor
from tangolib.processors import core, codeactive
from tangolib.generators.latex.latexconfig import LatexConfiguration
from tangolib.generators.latex.latexgen import LatexDocumentGenerator

def tangoArgumentParser():
    parser = argparse.ArgumentParser(prog="tango", description="a programmable document processor")

    parser.add_argument("input_file", type=str, help="input file", action="store")

    parser.add_argument("--banner", help="show nice banner", action="store_true")

    parser.add_argument("--latex", help="output latex", action="store_true")

    parser.add_argument("--codeactive", help="support for active python code", action="store_true")

    parser.add_argument("--output-dir", type=str, default="tango_output", help="set output directory", action="store")

    return parser
    

def tangoBanner():
    return \
r"""

                         .~""~.,--.       TANGO                       |
                          > :::i_, ~;                                 |
              mmn        <, ?::j~?`_{}          a Programmable        |
              (_)         l_  fl_ f {}                                |
               \ `.     ,__}--{_/_l___.      Document                 |
                \  `--~'           `m,_`.                             |
                 \                      )}           Processor        |
                  `~----f     i  :-----~'                             |
                        }     |  |-'/                                 |
________________________|     !  | f__________________________________!
                        l        j |                                   \
                        }==I===I={~(                                    \
                        f.       1( )                                    \
                        |      } }` `.                                    \
                        |     '  { ) )                                     \
                        }    f   |(  `\                                     \
                        |    |   |  )  )
                        |    |   |.  ( `.
                        |    |  ,l ) `. )
                       /{    |    \   ( `\
                      ('|    |\    \ ; `. )
                     (;!|    |`\    \  ',' )
                      YX|    |XX\    \XXXXXY
                        !____j_) \__,'> _)         (C) 2013 Frederic Peschanski
                     ,_.'`--('Y,_' ,^' /`!               
                     L___-__J  L_,'`--'     mab'95

"""

def tangoPrint(*args, echo=True):
    if echo:
        print("[Tango] ", end='')
    print(*args, end='')

def tangoPrintln(*args, echo=True):
    if echo:
        print("[Tango] ", end='')
    print(*args)
    
def tangoErr(*args):
    print(*args, file=sys.stderr, end='')

def tangoErrln(*args):
    print(*args, file=sys.stderr)

def fatal(*args):
    tangoErrln(*args)
    tangoErrln(" ==> aborpting ...")
    sys.exit(1)

if __name__ == "__main__":

    tangoPrintln("""   ______                      
  /_  __/___ _____  ____ _____ 
   / / / __ `/ __ \/ __ `/ __ \  Programmable Document Processor v0.1
  / / / /_/ / / / / /_/ / /_/ /
 /_/  \__,_/_/ /_/\__, /\____/   (C) 2013 F.Peschanski (see LICENSE)
                 /____/        
---""", echo=False)

    arg_parser = tangoArgumentParser()
    args = arg_parser.parse_args()

    if args.banner:
        print(tangoBanner())

    enable_process_phase = True
        
    if enable_process_phase:
        tangoPrintln("Process phase enabled")

    enable_generate_phase = True
    if not enable_process_phase:
        enable_generate_phase = False

    if enable_generate_phase:
        tangoPrintln("Generate phase enabled")

    latex_config = None
    enable_write_phase = False
    if args.latex:
        enable_write_phase = True
        latex_config = LatexConfiguration()

    if not enable_generate_phase:
        enable_write_phase = False

    if enable_write_phase:
        tangoPrintln("Write phase enabled")

    import os
    tangoPrintln("Current work directory = '{}'".format(os.getcwd()))

    # 1) parsing

    parser = Parser()

    tangoPrintln("Parsing from file '{}'".format(args.input_file))

    doc = parser.parse_from_file(args.input_file)

    # 2) processing

    if enable_process_phase:

        processor = DocumentProcessor(doc)
        core.register_core_processors(processor)

        # support for active python code
        if args.codeactive:
            tangoPrintln("Enabling active python code processors")

            py_ctx = codeactive.PythonContext()
            codeactive.register_processors(processor, py_ctx)

        try:
            processor.process()
        except codeactive.CheckPythonFailure as e:
            tangoErrln("CheckPython failed ...")
            fatal(str(e))

    # 3) generating

    generator = None
    
    if enable_generate_phase:

        if args.latex:
            # latex mode
            tangoPrintln("Generating latex")
            
            generator = LatexDocumentGenerator(doc, latex_config)
            generator.straighten_configuration()
            
        if not generator:
            fatal("No generator set")
            

        generator.generate()
        
    # 4) writing

    if enable_write_phase:

        if args.latex:
            output_mode_dir = "tex"
           
        output_directory = args.output_dir + "/" + output_mode_dir
 
        try:
            os.makedirs(output_directory)
        except OSError:
            tangoPrint("Using ")
        else:
            tangoPrint("Creating ")

        tangoPrintln("output directory '{}'".format(output_directory))

        infile_without_ext = args.input_file.split(".")
        if infile_without_ext[-1] == "tex":
            infile_without_ext = ".".join(infile_without_ext[:-1])
        else:
            infile_without_ext = args.input_file

        main_output_filename = output_directory + "/" + infile_without_ext + "-gen." + output_mode_dir

        tangoPrintln("Writing main {} file '{}'".format(output_mode_dir, main_output_filename))

        main_output_file = open(main_output_filename, 'w')
        main_output_file.write(str(generator.output))
        main_output_file.close()


    print("... bye bye ...")


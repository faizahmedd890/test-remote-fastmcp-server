import os
import shutil
import subprocess

from mcp.server.fastmcp import FastMCP


# --------------------------------------------------
# Create MCP server
# --------------------------------------------------

mcp = FastMCP("manim-server")


# --------------------------------------------------
# Manim executable
# --------------------------------------------------

# You can either:
# 1. Put "manim" if Manim is available in PATH
# 2. Put the complete path to manim.exe

MANIM_EXECUTABLE = os.getenv(
    "MANIM_EXECUTABLE",
    r"C:\Users\faiza\AppData\Local\Programs\Python\Python310\Scripts\manim.exe"
)


# --------------------------------------------------
# Directories
# --------------------------------------------------

BASE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "media"
)

os.makedirs(BASE_DIR, exist_ok=True)

TEMP_DIRS = {}


# --------------------------------------------------
# Execute Manim
# --------------------------------------------------

@mcp.tool()
def execute_manim_code(manim_code: str) -> str:
    """
    Execute Manim Python code and render the animation.
    """

    # Directory where the temporary Manim project will live
    tmpdir = os.path.join(BASE_DIR, "manim_tmp")

    os.makedirs(tmpdir, exist_ok=True)

    # Python file containing the Manim code
    script_path = os.path.join(tmpdir, "scene.py")

    try:

        # ------------------------------------------
        # Write Manim code to scene.py
        # ------------------------------------------

        with open(
            script_path,
            "w",
            encoding="utf-8"
        ) as script_file:

            script_file.write(manim_code)


        # ------------------------------------------
        # Run Manim
        # ------------------------------------------
        #
        # IMPORTANT:
        #
        # We use -ql instead of -p
        #
        # -q = quality
        # -l = low quality
        #
        # We DON'T use -p because -p tries to open
        # the rendered video in a preview application.
        #
        # That can cause the MCP tool to wait and
        # eventually timeout.
        #
        # ------------------------------------------

        result = subprocess.run(
            [
                MANIM_EXECUTABLE,
                "-ql",
                script_path
            ],
            capture_output=True,
            text=True,
            cwd=tmpdir,
            timeout=120
        )


        # ------------------------------------------
        # Manim succeeded
        # ------------------------------------------

        if result.returncode == 0:

            TEMP_DIRS[tmpdir] = True

            return (
                "Execution successful.\n\n"
                f"Manim output directory:\n{tmpdir}\n\n"
                "The animation was rendered successfully."
            )


        # ------------------------------------------
        # Manim failed
        # ------------------------------------------

        else:

            return (
                "Manim execution failed.\n\n"
                f"Return code: {result.returncode}\n\n"
                f"STDOUT:\n{result.stdout}\n\n"
                f"STDERR:\n{result.stderr}"
            )


    # ----------------------------------------------
    # Manim took too long
    # ----------------------------------------------

    except subprocess.TimeoutExpired:

        return (
            "Manim execution timed out after 120 seconds.\n\n"
            "The Manim process may be stuck or the "
            "animation may be too heavy."
        )


    # ----------------------------------------------
    # Other error
    # ----------------------------------------------

    except Exception as e:

        return (
            f"Error during Manim execution:\n{str(e)}"
        )


# --------------------------------------------------
# Cleanup Manim temporary directory
# --------------------------------------------------

@mcp.tool()
def cleanup_manim_temp_dir(directory: str) -> str:
    """
    Delete a Manim temporary directory.
    """

    try:

        if os.path.exists(directory):

            shutil.rmtree(directory)

            return (
                f"Cleanup successful for directory: "
                f"{directory}"
            )

        else:

            return (
                f"Directory not found: {directory}"
            )


    except Exception as e:

        return (
            f"Failed to clean up directory: "
            f"{directory}\n\n"
            f"Error: {str(e)}"
        )


# --------------------------------------------------
# Start MCP server
# --------------------------------------------------

if __name__ == "__main__":

    mcp.run(transport="stdio")
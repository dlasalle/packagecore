##
# @file docker.py
# @brief Wrapper for utilizing docker containers.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03


import os
import shutil
import sys
import random
import time
from subprocess import Popen, PIPE


USERNAME = "builder"


def _makeDir(path):
  try:
    os.makedirs(path, 0o700)
  except FileExistsError as e:
    pass


class InputError(Exception):
  pass


class DockerError(Exception):
  pass


def _checkedDockerCommand(cmd):
  rc = _uncheckedDockerCommand(cmd) 
  if rc != 0:
    raise DockerError("Command '%s' returned %d." % (cmd, rc))


def _uncheckedDockerCommand(cmd):
  proc = Popen(["docker"] + cmd)
  rc = proc.wait()
  return rc




class MockContainer(object):
  def __init__(self):
    _makeDir(self.getSharedDir())

  def execute(self, cmd, cwd=None):
    pass


  def getSharedDir(self):
    return "/tmp/mock-dir"


  def copySource(self):
    pass


  def getSourceDir(self):
    return os.path.join(self.getSharedDir(),"src")


  def getImageName(self):
    return "linux:2.6"


  def stop(self):
    pass


class DockerContainer(object):
  ##
  # @brief Create a new docker container (left running).
  #
  # @param imageName The image to create it from.
  #
  # @return The docker container.
  def __init__(self, imageName):
    self._image = imageName
    # get a unique name
    self._name = "packagecore-%x" % random.randrange(0,2**64)

    # make the shared directory
    if os.path.exists(self.getSharedDir()):
      shutil.rmtree(self.getSharedDir())
    _makeDir(self.getSharedDir())

    print("Starting docker container '%s'." % self._name)

    # hack to keep the container running
    self._proc = Popen(["docker", "run", "--name", self._name, "-v", \
        "%s:%s" % (self.getSharedDir(), self.getSharedDir()), \
        self._image, "tail", "-f", "/dev/null"])

    # wait for our container to start
    running = False
    waitCycles = 0
    while self._proc.poll() is None:
      time.sleep(1)
      p = Popen(["docker ps | grep '%s'" % self._name], shell=True)
      rc = p.wait()
      if rc == 0:
        running = True
        break
      waitCycles += 1
      if waitCycles > 10:
        self._proc.kill()
        break
    if not running:
      # try to cleanup a bit before we exit
      self.stop()
      raise DockerError("Container failed to start: %s" % self._name)


  ##
  # @brief Execute a command in the container.
  #
  # @param cmd The command to execute.
  #
  # @return None
  def execute(self, cmd):
    if isinstance(cmd, str):
      cmd=[cmd]
    if not isinstance(cmd, list):
      raise InputError("Requires list of commands, not '%s'" % type(cmd))
    _checkedDockerCommand(["exec", self._name] + cmd)


  ##
  # @brief Get the directory shared between the host and the container.
  #
  # @return The shared directory (inside and outside of the container).
  def getSharedDir(self):
    return os.path.join("/tmp", self._name)


  ##
  # @brief Copy a directory of source code to inside of the container.
  #
  # @param localPath Where the source directory currently resides.
  #
  # @return None
  def copySource(self, localPath):
    shutil.copytree(localPath, self.getSourceDir()) 


  ##
  # @brief Get the source directory path inside of the container.
  #
  # @return 
  def getSourceDir(self):
    return os.path.join(self.getSharedDir(), "src")


  ##
  # @brief Get the name of the underlying docker image.
  #
  # @return 
  def getImageName(self):
    return self._image


  ##
  # @brief Get the running container's name.
  #
  # @return The name.
  def getName(self):
    return self._name


  def stop(self):
    print("Cleaning up self %s." % self.getName())
    # kill the running self
    _uncheckedDockerCommand(["kill", self.getName()])

    # remove self
    _uncheckedDockerCommand(["rm", self.getName()])

    # remove image -- later may be a preference to keep it
    #_uncheckedDockerCommand(["rmi", self.getImageName()])

    # remove shared directory
    try:
      if "BP_LEAVE_FILES" in os.environ:
        pass
      else:
        shutil.rmtree(self.getSharedDir())
    except:
      print("Warning: failed to remove shared directory.", file=sys.stderr)





class Docker(object):
  ##
  # @brief Initialize a new docker wrapper.
  #
  # @return The new Docker wrapper. 
  def __init__(self):
    pass


  ##
  # @brief Download the specified image.
  #
  # @param image The name of the docker image.
  #
  # @return None
  def __fetchImage(self, image):
    _checkedDockerCommand(["pull", image])


  ##
  # @brief Start an image.
  #
  # @param dockerImage The name of the image to start.
  #
  # @return The started container. 
  def start(self, dockerImage):
    self.__fetchImage(dockerImage)
    return DockerContainer(dockerImage)


  ##
  # @brief Close the container (actualyl just delete the image).
  #
  # @param container The container.
  #
  # @return None
  def stop(self, container):
    container.stop()


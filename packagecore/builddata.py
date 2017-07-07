##
# @file builddata.py
# @brief Struct for holding build information.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-05-29


def generateMockData():
  data = BuildData("mypackage", "1.2.3", 2, "centos7", ["make"], \
      ["make install"], ["adduser -m test"], ["ls"])
  data.license = "MIT"
  data.homepage = "www.test.com"
  data.summary = "A really important and good package"
  data.maintainer = "me"
  data.buildDeps = ["cmake", "gcc"]
  data.runDeps = ["openssl", "glibc", "libwxgtk"]

  return data




class BuildData(object):
  def __init__(self, name, version, releaseNum, os, compileCommands, \
      installCommands, postInstallCommands, testInstallCommands):
    # we only want lower-case package names.
    self.name = name.lower()
    self.version = version
    self.releaseNum = releaseNum
    self.maintainer = "" 
    self.license = "Custom" 
    self.homepage = "" 
    self.summary = "none" 
    self.os = os
    self.buildDeps = []
    self.runDeps = [] 
    self.compileCommands = compileCommands
    self.installCommands = installCommands
    self.postInstallCommands = postInstallCommands
    self.testInstallCommands = testInstallCommands


  def __str__(self):
    return \
      """
      name: %s
      version: %s
      releaseNum: %d
      maintainer: %s
      license: %s
      homepage: %s
      summary: %s
      os: %s
      buildDeps: %s
      runDeps: %s
      compileCommands: %s
      installCommands: %s
      postInstallCommands: %s
      testInstallCommands: %s
      """ % (self.name, self.version, self.releaseNum, self.maintainer, \
        self.license, self.homepage, self.summary, self.os, self.buildDeps,
        self.runDeps, self.compileCommands, self.installCommands,
        self.postInstallCommands, self.testInstallCommands)

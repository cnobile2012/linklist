ifeq ($(findstring Windows_NT, $(OS) $(OSTYPE)),Windows_NT)
  OS = WIN32
else

  UNAME := $(shell uname -s)

  ifeq ($(UNAME),SunOS)
    OS = SOLARIS
  endif

  ifeq ($(UNAME),OSF)
    OS = OSF1
  endif

  ifeq ($(UNAME),OSF1)
    OS = OSF1
  endif

  ifeq ($(UNAME),linux)
    OS = LINUX
  endif

  ifeq ($(UNAME),Linux)
    OS = LINUX
  endif

  ifeq ($(UNAME),AIX)
    OS = AIX
  endif
endif

# ---------------------------------------------------------------------
# Makefile.user: Makefile for ESE examples
# ---------------------------------------------------------------------

# --- Default macros

CP      = 	cp -f
RM	=	rm -rf
NAME	=	test1

# -- Compilation

all: 
	@echo "only support [make clean]"

clean:
	$(RM) .tmp* result

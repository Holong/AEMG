# ---------------------------------------------------------------------
# Makefile.user: Makefile for ESE examples
# ---------------------------------------------------------------------

# --- Default macros


CP      = 	cp -f
RM	=	rm -rf
NAME	=	test

# -- Compilation

all: ftlm ttlm

platform:
	@echo "Running python script to finalize partial design"
	./main.py 
	@echo "Running python script to make eds"
	./$(NAME).py

ftlm: platform
	@echo "Generating SystemC functional TLM"
	tlmgen $(NAME).eds
	@echo "Compiling functional TLM"
	cd $(NAME)_functional_TLM && make
	@echo "Executing functional TLM"
	cd $(NAME)_functional_TLM && ./tlm

ttlm: platform
	@echo "Generating SystemC timed TLM"
	tlmest $(NAME).eds
	@echo "Compiling timed TLM"
	cd $(NAME)_timed_TLM && make
	@echo "Executing timed TLM"
	cd $(NAME)_timed_TLM && ./tlm

clean:
	$(RM) *.eds *.xml $(NAME)* .tmp*

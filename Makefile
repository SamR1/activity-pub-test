include Makefile.config
-include Makefile.custom.config
.SILENT:

clean-install:
	rm -fr $(VENV)

install:
	test -d $(VENV) || virtualenv $(VENV) -p $(PYTHON_VERSION)
	$(PIP) install -r requirements.txt

lint:
	$(BLACK) $(FLASK_APP)

serve:
	$(FLASK) run --with-threads -h $(HOST) -p $(API_PORT)

CAAS = cmd-as-a-service
TARGET = $(CAAS)/$(CAAS)

all: $(TARGET)

$(TARGET): $(wildcard $(CAAS)/*.go)
	cd $(CAAS); go build
clean:
	$(RM) $(TARGET)

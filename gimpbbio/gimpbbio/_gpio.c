#include "Python.h"
#include "stdio.h"

// python function value = read(file_descriptor)
static PyObject *py_read_gpio(PyObject *self, PyObject *args)
{
    int file_descriptor;
    char buffer;
    int value;
    int bytes_read;
    PyObject *py_value;

    if (!PyArg_ParseTuple(args, "i", &file_descriptor))
        return NULL;

    bytes_read = pread(file_descriptor, &buffer, sizeof(buffer), 0);

    if (bytes_read == 0)
    {
        PyErr_SetString(PyExc_IOError, "Could not read pin value.");
        return NULL;
    }

    // Convert to integer because it's going to be more performant than
    // allocing and returning a Python string
    value = buffer != '0' ? 1 : 0;
    py_value = Py_BuildValue("i", value);

    return py_value;
}

// python function value = write(file_descriptor, value)
static PyObject *py_write_gpio(PyObject *self, PyObject *args)
{
    int file_descriptor;
    int value;
    char buffer;
    int bytes_written;

    if (!PyArg_ParseTuple(args, "ip", &file_descriptor, &value))
        return NULL;

    buffer = value ? '1' : '0';

    bytes_written = pwrite(file_descriptor, &buffer, sizeof(buffer), 0);

    if (bytes_written == 0)
    {
        PyErr_SetString(PyExc_IOError, "Could not write pin value.");
        return NULL;
    }

    Py_RETURN_NONE;
}

static const char moduledocstring[] = "GPIO reading and writing functionality for BeagleBone";

PyMethodDef gpio_methods[] = {
   {"read", py_read_gpio, METH_VARARGS, "Read from a GPIO device tree file.  Returns HIGH=1=True or LOW=0=False\nfile_descriptor - file descriptor obtained from os.open"},
   {"write", py_write_gpio, METH_VARARGS, "Write to a GPIO device tree file\nfile_descriptor - file descriptor obtained from os.open\nvalue - truthy to set the pin high, falsey to set it low"},
   {NULL, NULL, 0, NULL}
};

static struct PyModuleDef gpiomodule = {
   PyModuleDef_HEAD_INIT,
   "_gpio",       // name of module
   moduledocstring,  // module documentation, may be NULL
   -1,               // size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
   gpio_methods
};

PyMODINIT_FUNC PyInit__gpio(void)
{
   PyObject *module = NULL;

   if ((module = PyModule_Create(&gpiomodule)) == NULL)
      return NULL;

   return module;
}

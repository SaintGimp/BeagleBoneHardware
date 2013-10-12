#include "Python.h"
#include "stdio.h"

// python function value = read(file_descriptor)
static PyObject *py_read_gpio(PyObject *self, PyObject *args)
{
    int *file_descriptor;
    char buffer;
    int value;
    int bytes_read;
    PyObject *py_value;

    if (!PyArg_ParseTuple(args, "i", &file_descriptor))
        return NULL;

    bytes_read = pread(*file_descriptor, &buffer, sizeof(buffer), 0);

    if (bytes_read == 0)
        PyErr_SetString(PyExc_IOError, "Could not read pin value.");
      
    value = buffer != '0' ? 1 : 0;
    py_value = Py_BuildValue("i", value);

    return py_value;
}

static const char moduledocstring[] = "GPIO reading and writing functionality for BeagleBone";

PyMethodDef gpio_methods[] = {
   {"read", py_read_gpio, METH_VARARGS, "Read from a GPIO device tree file.  Returns HIGH=1=True or LOW=0=False\ngpio - gpio channel"},
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

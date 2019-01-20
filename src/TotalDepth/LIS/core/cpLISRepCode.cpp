//
//  cpLISRepCode.c
//  TotalDepth
//
//  Created by Paul Ross on 13/01/2019.
//  Copyright © 2019 Engineering UN. All rights reserved.
//
#include "Python.h"

#include "cpLISRepCode.h"
#include "LISRepCode.h"

static PyObject *from68(PyObject *module, PyObject *arg) {
    PyObject *ret = NULL;
    long word;
    assert(arg);
    assert(! PyErr_Occurred());
    /* Treat arg as a borrowed reference. */
    Py_INCREF(arg);
    if (! PyLong_Check(arg)) {
        PyErr_Format(PyExc_ValueError,
                     "%s() in %s#%d takes and float or an int not a \"%s\"",
                     __FUNCTION__, __FILE__, __LINE__,
                     Py_TYPE(arg)->tp_name);
        goto except;
    }
    word = PyLong_AsLong(arg);
    ret = PyFloat_FromDouble(_from68(static_cast<int32_t>(word & 0xFFFFFFFF)));
    if (! ret) {
        PyErr_Format(PyExc_RuntimeError,
                     "%s() in %s#%d: Can not create a float.",
                     __FUNCTION__, __FILE__, __LINE__);
        goto except;
    }
    assert(! PyErr_Occurred());
    assert(ret);
    goto finally;
except:
    assert(PyErr_Occurred());
    Py_XDECREF(ret);
    ret = NULL;
finally:
    /* Treat arg as a borrowed reference. */
    Py_DECREF(arg);
    return ret;
}

static PyObject *to68(PyObject *module, PyObject *arg) {
    PyObject *ret = NULL;
    double value;
    int32_t as_68;
//    long as_68_l;
    assert(arg);
    assert(! PyErr_Occurred());
    /* Treat arg as a borrowed reference. */
    Py_INCREF(arg);
    if (PyFloat_Check(arg)) {
        value = PyFloat_AsDouble(arg);
    } else if (PyLong_Check(arg)) {
        value = PyLong_AsLong(arg);
    } else {
        PyErr_Format(PyExc_ValueError,
                     "%s() in %s#%d takes and float or an int not a \"%s\"",
                     __FUNCTION__, __FILE__, __LINE__,
                     Py_TYPE(arg)->tp_name);
        goto except;
    }
    as_68 = _to68(value);
    ret = PyLong_FromLong(as_68);
    if (! ret) {
        PyErr_Format(PyExc_RuntimeError,
                     "%s() in %s#%d: Can not create a long.",
                     __FUNCTION__, __FILE__, __LINE__);
        goto except;
    }
    assert(! PyErr_Occurred());
    assert(ret);
    goto finally;
except:
    assert(PyErr_Occurred());
    Py_XDECREF(ret);
    ret = NULL;
finally:
    /* Treat arg as a borrowed reference. */
    Py_DECREF(arg);
    return ret;
}

static PyMethodDef cpRepCode_methods[] = {
    {"from68", (PyCFunction)from68, METH_O,
        "Converts a 32bit integer word with representation code 68 to a float."
    },
    {"to68", (PyCFunction)to68, METH_O,
        "Converts a float to a 32bit integer word with representation code 68."
    },
    /* Other functions here... */
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

/* Module specification. */
static PyModuleDef cpRepCodemodule = {
    PyModuleDef_HEAD_INIT,
    "cpRepCode",
    "CPython extension to convert representation codes.",
    -1,     /* m_size - support for sub-interpreters. */
    cpRepCode_methods,
    NULL, /* m_slots - An array of slot definitions for multi-phase initialization. */
    NULL, /* m_traverse - A traversal function to call during GC traversal of the module object. */
    NULL, /* m_clear - A clear function to call during GC clearing of the module object. */
    NULL  /* m_free - A function to call during deallocation of the module object. */
};

PyMODINIT_FUNC
PyInit_cpRepCode(void)
{
    PyObject *m= PyModule_Create(&cpRepCodemodule);
    if (m == NULL) {
        return NULL;
    }
    /* Possible other initialisations of globals or exceptions. */
    return m;
}

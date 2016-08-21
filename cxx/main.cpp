#include "Python.h"
// #include "numpy/arrayobject.h"
#include <iostream>
#include <string>
#include <stdexcept>
#include <new>
using namespace std;
const bool debug = true;

/* 
 * get origin and spacing of all grids on level "level" at "frame"
 * result[] should has a length of 6*number_of_grids_on_this_level
 * return result[]
 */
void getAllOriginsAndSpacing(int frame, int level, double* result)
{
    PyObject *pName2, *pModule2, *pDict2, *pFunc2;
    PyObject *pArgs2, *pValue2;
    // Name of python files
    char pythonFile[] = "py_function";
    // python functions to be called
    char getAllOriginsAndSpacing[] = "getAllOriginsAndSpacing";

    // Py_Initialize();
    pName2 = PyString_FromString(pythonFile);
    pModule2 = PyImport_Import(pName2);
    pDict2 = PyModule_GetDict(pModule2);
    pFunc2 = PyDict_GetItemString(pDict2, getAllOriginsAndSpacing);
    // Arguments passed to python function
    pArgs2 = PyTuple_New(2);
    PyTuple_SetItem(pArgs2, 0, PyInt_FromLong(frame));
    PyTuple_SetItem(pArgs2, 1, PyInt_FromLong(level));
    if (pFunc2 && PyCallable_Check(pFunc2)) 
    {
        pValue2 = PyObject_CallObject(pFunc2, pArgs2);
    } 
    else 
    {
        PyErr_Print();
    }
    int resultSize = PyList_Size(pValue2);
    if (pValue2 != NULL && PyList_Check(pValue2)) {
        cout<<"Receiving origin and spacing info from python."<<endl;
        for ( int i = 0; i < resultSize; i++ )
        {
            result[i] = PyFloat_AsDouble(PyList_GetItem(pValue2, i));
        }
    }
    else 
    {
        PyErr_Print();
    }
    if (debug)
    {
        cout<<"Get Origin and Spacing infomation of all grids on level: "<<level<<endl;
        for ( int g = 0; g < (resultSize+1)/6; g++)
        {
            cout<<"Origin: ("<<result[g*6]<<" "<<result[g*6+1]<<" "<<result[g*6+2]<<")"<<endl;
            cout<<"Spacing: ("<<result[g*6+3]<<" "<<result[g*6+4]<<" "<<result[g*6+5]<<")"<<endl;
        }
    }
    cout<<"\n"<<endl;
    // Clean up
    Py_DECREF(pName2);
    Py_DECREF(pModule2);
    Py_DECREF(pDict2);
    Py_DECREF(pFunc2);
    Py_DECREF(pArgs2);
    Py_DECREF(pValue2);
    // Py_Finalize();

}

void getLevels(int frame, int* numLevelsPtr, int** blocksPerLevelPtr)
{
    PyObject *pName, *pModule, *pDict, *pFunc;
    PyObject *pArgs, *pValue;

    // Name of python files
    char pythonFile[] = "py_function";
    // python functions to be called
    char getLevels[] = "getLevels";

    // Initialize the Python Interpreter
    // Py_Initialize();

    // Build the name object
    pName = PyString_FromString(pythonFile);
    //pName = PyString_FromString(argv[1]);

    // Load the module object
    pModule = PyImport_Import(pName);

    // pDict is a borrowed reference 
    pDict = PyModule_GetDict(pModule);

    // pFunc is also a borrowed reference 
    pFunc = PyDict_GetItemString(pDict, getLevels);

    // Arguments passed to python function
    pArgs = PyTuple_New(1);
    PyTuple_SetItem(pArgs, 0, PyInt_FromLong(frame));

    if (pFunc && PyCallable_Check(pFunc)) 
    {
        pValue = PyObject_CallObject(pFunc, pArgs);
    } 
    else 
    {
        PyErr_Print();
    }

    // int* blocksPerLevelPtr;
    if (pValue != NULL && PyList_Check(pValue)) {
        *numLevelsPtr = PyList_Size(pValue);
        try
        {
            *blocksPerLevelPtr = new int [*numLevelsPtr];
        }
        catch(bad_alloc& err)
        {
            cout<<"Failed to alloc memory to blocksPerLevel:"<<err.what()<<endl;
        }
        for ( int i = 0; i < *numLevelsPtr; i++ )
        {
            (*blocksPerLevelPtr)[i] = PyFloat_AsDouble(PyList_GetItem(pValue, i));
            cout<<"Level "<<i<<" has "<<(*blocksPerLevelPtr)[i]<<" grids."<<endl;
        }
    }
    else 
    {
        PyErr_Print();
    }
    cout<<"\n"<<endl;

    // Clean up
    Py_DECREF(pName);
    Py_DECREF(pModule);
    Py_DECREF(pDict);
    Py_DECREF(pFunc);
    Py_DECREF(pArgs);
    Py_DECREF(pValue);
    // Py_Finalize();

}
void clean_getLevels(int** blocksPerLevel)
{
    delete *blocksPerLevel;
}
/*
 * Assume each time we gennerate a clawpack solution object
 * from the same frame, the states list (after sorted by level)
 * has the same order
 */
int main(int argc, char *argv[])
{
    Py_Initialize();
    int numLevels = 0; // number of levels
    // get numLevels and number of grids on each level
    int* blocksPerLevel; //dynamic array
    int frame = 3;
    getLevels(frame, &numLevels, &blocksPerLevel);

    // check if I get numLevels and blocksPerLevel after the call
    cout<<"After calling getLevels, we have:"<<endl;
    cout<<"numLevels = "<<numLevels<<endl;
    for ( int i = 0; i < 3; i++ )
    {
        cout<<"Level "<<i<<" has "<<blocksPerLevel[i]<<" grids."<<endl;
    }
    cout<<"\n"<<endl;
    clean_getLevels(&blocksPerLevel);


    double* result = new double [24];
    getAllOriginsAndSpacing(3,1, result);
    delete result;


    //clean up
    Py_Finalize();
    return 0;
}

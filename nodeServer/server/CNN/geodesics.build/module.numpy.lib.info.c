/* Generated code for Python source for module 'numpy.lib.info'
 * created by Nuitka version 0.5.32.7
 *
 * This code is in part copyright 2018 Kay Hayen.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "nuitka/prelude.h"

#include "__helpers.h"

/* The _module_numpy$lib$info is a Python object pointer of module type. */

/* Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_numpy$lib$info;
PyDictObject *moduledict_numpy$lib$info;

/* The module constants used, if any. */
extern PyObject *const_str_plain___file__;
static PyObject *const_str_digest_88ae6ea843d3bbe13a8b01b587485e64;
extern PyObject *const_str_plain_global_symbols;
extern PyObject *const_str_plain_testing;
static PyObject *const_list_str_plain_core_str_plain_testing_list;
static PyObject *const_str_digest_f89d5e2441d80b29b22ac56aab63c345;
extern PyObject *const_str_chr_42;
extern PyObject *const_str_plain_absolute_import;
extern PyObject *const_str_plain_core;
static PyObject *const_str_digest_410b05d2a9a14659b01e6d2ad73b4d66;
extern PyObject *const_list_str_chr_42_list;
extern PyObject *const_str_plain_depends;
extern PyObject *const_tuple_empty;
extern PyObject *const_str_plain___doc__;
extern PyObject *const_str_plain___cached__;
extern PyObject *const_str_plain_division;
extern PyObject *const_str_plain_print_function;
static PyObject *const_str_digest_7d8134536515680674da910bddb241f8;
static PyObject *module_filename_obj;

static bool constants_created = false;

static void createModuleConstants( void )
{
    const_str_digest_88ae6ea843d3bbe13a8b01b587485e64 = UNSTREAM_STRING( &constant_bin[ 826842 ], 17, 0 );
    const_list_str_plain_core_str_plain_testing_list = PyList_New( 2 );
    PyList_SET_ITEM( const_list_str_plain_core_str_plain_testing_list, 0, const_str_plain_core ); Py_INCREF( const_str_plain_core );
    PyList_SET_ITEM( const_list_str_plain_core_str_plain_testing_list, 1, const_str_plain_testing ); Py_INCREF( const_str_plain_testing );
    const_str_digest_f89d5e2441d80b29b22ac56aab63c345 = UNSTREAM_STRING( &constant_bin[ 826859 ], 23, 0 );
    const_str_digest_410b05d2a9a14659b01e6d2ad73b4d66 = UNSTREAM_STRING( &constant_bin[ 826882 ], 6490, 0 );
    const_str_digest_7d8134536515680674da910bddb241f8 = UNSTREAM_STRING( &constant_bin[ 826867 ], 14, 0 );

    constants_created = true;
}

#ifndef __NUITKA_NO_ASSERT__
void checkModuleConstants_numpy$lib$info( void )
{
    // The module may not have been used at all.
    if (constants_created == false) return;


}
#endif

// The module code objects.
static PyCodeObject *codeobj_7e5c1f9ebdac02e5fbab2b23ff460504;

static void createModuleCodeObjects(void)
{
    module_filename_obj = MAKE_RELATIVE_PATH( const_str_digest_88ae6ea843d3bbe13a8b01b587485e64 );
    codeobj_7e5c1f9ebdac02e5fbab2b23ff460504 = MAKE_CODEOBJ( module_filename_obj, const_str_digest_f89d5e2441d80b29b22ac56aab63c345, 1, const_tuple_empty, 0, 0, CO_NOFREE );
}

// The module function declarations.


// The module function definitions.



#if PYTHON_VERSION >= 300
static struct PyModuleDef mdef_numpy$lib$info =
{
    PyModuleDef_HEAD_INIT,
    "numpy.lib.info",   /* m_name */
    NULL,                /* m_doc */
    -1,                  /* m_size */
    NULL,                /* m_methods */
    NULL,                /* m_reload */
    NULL,                /* m_traverse */
    NULL,                /* m_clear */
    NULL,                /* m_free */
  };
#endif

extern PyObject *const_str_plain___package__;

#if PYTHON_VERSION >= 300
extern PyObject *const_str_dot;

extern PyObject *const_str_plain___loader__;
extern PyObject *metapath_based_loader;
#endif

#if PYTHON_VERSION >= 340
extern PyObject *const_str_plain___spec__;
#endif

extern void _initCompiledCellType();
extern void _initCompiledGeneratorType();
extern void _initCompiledFunctionType();
extern void _initCompiledMethodType();
extern void _initCompiledFrameType();
#if PYTHON_VERSION >= 350
extern void _initCompiledCoroutineTypes();
#endif
#if PYTHON_VERSION >= 360
extern void _initCompiledAsyncgenTypes();
#endif

// The exported interface to CPython. On import of the module, this function
// gets called. It has to have an exact function name, in cases it's a shared
// library export. This is hidden behind the MOD_INIT_DECL.

MOD_INIT_DECL( numpy$lib$info )
{
#if defined(_NUITKA_EXE) || PYTHON_VERSION >= 300
    static bool _init_done = false;

    // Modules might be imported repeatedly, which is to be ignored.
    if ( _init_done )
    {
        return MOD_RETURN_VALUE( module_numpy$lib$info );
    }
    else
    {
        _init_done = true;
    }
#endif

#ifdef _NUITKA_MODULE
    // In case of a stand alone extension module, need to call initialization
    // the init here because that's the first and only time we are going to get
    // called here.

    // Initialize the constant values used.
    _initBuiltinModule();
    createGlobalConstants();

    /* Initialize the compiled types of Nuitka. */
    _initCompiledCellType();
    _initCompiledGeneratorType();
    _initCompiledFunctionType();
    _initCompiledMethodType();
    _initCompiledFrameType();
#if PYTHON_VERSION >= 350
    _initCompiledCoroutineTypes();
#endif
#if PYTHON_VERSION >= 360
    _initCompiledAsyncgenTypes();
#endif

#if PYTHON_VERSION < 300
    _initSlotCompare();
#endif
#if PYTHON_VERSION >= 270
    _initSlotIternext();
#endif

    patchBuiltinModule();
    patchTypeComparison();

    // Enable meta path based loader if not already done.
#ifdef _NUITKA_TRACE
    puts("numpy.lib.info: Calling setupMetaPathBasedLoader().");
#endif
    setupMetaPathBasedLoader();

#if PYTHON_VERSION >= 300
    patchInspectModule();
#endif

#endif

    /* The constants only used by this module are created now. */
#ifdef _NUITKA_TRACE
    puts("numpy.lib.info: Calling createModuleConstants().");
#endif
    createModuleConstants();

    /* The code objects used by this module are created now. */
#ifdef _NUITKA_TRACE
    puts("numpy.lib.info: Calling createModuleCodeObjects().");
#endif
    createModuleCodeObjects();

    // puts( "in initnumpy$lib$info" );

    // Create the module object first. There are no methods initially, all are
    // added dynamically in actual code only.  Also no "__doc__" is initially
    // set at this time, as it could not contain NUL characters this way, they
    // are instead set in early module code.  No "self" for modules, we have no
    // use for it.
#if PYTHON_VERSION < 300
    module_numpy$lib$info = Py_InitModule4(
        "numpy.lib.info",       // Module Name
        NULL,                    // No methods initially, all are added
                                 // dynamically in actual module code only.
        NULL,                    // No "__doc__" is initially set, as it could
                                 // not contain NUL this way, added early in
                                 // actual code.
        NULL,                    // No self for modules, we don't use it.
        PYTHON_API_VERSION
    );
#else

    module_numpy$lib$info = PyModule_Create( &mdef_numpy$lib$info );
#endif

    moduledict_numpy$lib$info = MODULE_DICT( module_numpy$lib$info );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        PyObject *module_name = GET_STRING_DICT_VALUE( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___name__ );

        UPDATE_STRING_DICT1(
            moduledict_numpy$lib$info,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );

#else

#if PYTHON_VERSION < 300
        PyObject *module_name = GET_STRING_DICT_VALUE( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___name__ );
        char const *module_name_cstr = PyString_AS_STRING( module_name );

        char const *last_dot = strrchr( module_name_cstr, '.' );

        if ( last_dot != NULL )
        {
            UPDATE_STRING_DICT1(
                moduledict_numpy$lib$info,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize( module_name_cstr, last_dot - module_name_cstr )
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___name__ );
        Py_ssize_t dot_index = PyUnicode_Find( module_name, const_str_dot, 0, PyUnicode_GetLength( module_name ), -1 );

        if ( dot_index != -1 )
        {
            UPDATE_STRING_DICT1(
                moduledict_numpy$lib$info,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring( module_name, 0, dot_index )
            );
        }
#endif
#endif
    }

    CHECK_OBJECT( module_numpy$lib$info );

// Seems to work for Python2.7 out of the box, but for Python3, the module
// doesn't automatically enter "sys.modules", so do it manually.
#if PYTHON_VERSION >= 300
    {
        int r = PyObject_SetItem( PySys_GetObject( (char *)"modules" ), const_str_digest_7d8134536515680674da910bddb241f8, module_numpy$lib$info );

        assert( r != -1 );
    }
#endif

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if ( GET_STRING_DICT_VALUE( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___builtins__ ) == NULL )
    {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if !defined(_NUITKA_EXE) || !0
        value = PyModule_GetDict( value );
#endif

        UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___builtins__, value );
    }

#if PYTHON_VERSION >= 300
    UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___loader__, metapath_based_loader );
#endif

#if PYTHON_VERSION >= 340
#if 0
    UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___spec__, Py_None );
#else
    {
        PyObject *bootstrap_module = PyImport_ImportModule("importlib._bootstrap");
        CHECK_OBJECT( bootstrap_module );
        PyObject *module_spec_class = PyObject_GetAttrString( bootstrap_module, "ModuleSpec" );
        Py_DECREF( bootstrap_module );

        PyObject *args[] = {
            GET_STRING_DICT_VALUE( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___name__ ),
            metapath_based_loader
        };

        PyObject *spec_value = CALL_FUNCTION_WITH_ARGS2(
            module_spec_class,
            args
        );

        UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___spec__, spec_value );

        Py_DECREF( module_spec_class );
    }
#endif
#endif


    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    PyObject *exception_type = NULL;
    PyObject *exception_value = NULL;
    PyTracebackObject *exception_tb = NULL;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *exception_keeper_type_1;
    PyObject *exception_keeper_value_1;
    PyTracebackObject *exception_keeper_tb_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    PyObject *tmp_assign_source_1;
    PyObject *tmp_assign_source_2;
    PyObject *tmp_assign_source_3;
    PyObject *tmp_assign_source_4;
    PyObject *tmp_assign_source_5;
    PyObject *tmp_assign_source_6;
    PyObject *tmp_assign_source_7;
    PyObject *tmp_assign_source_8;
    PyObject *tmp_assign_source_9;
    PyObject *tmp_import_name_from_1;
    PyObject *tmp_import_name_from_2;
    PyObject *tmp_import_name_from_3;
    struct Nuitka_FrameObject *frame_7e5c1f9ebdac02e5fbab2b23ff460504;

    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;

    // Module code.
    tmp_assign_source_1 = const_str_digest_410b05d2a9a14659b01e6d2ad73b4d66;
    UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___doc__, tmp_assign_source_1 );
    tmp_assign_source_2 = module_filename_obj;
    UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___file__, tmp_assign_source_2 );
    tmp_assign_source_3 = Py_None;
    UPDATE_STRING_DICT0( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain___cached__, tmp_assign_source_3 );
    tmp_assign_source_4 = PyImport_ImportModule("__future__");
    assert( !(tmp_assign_source_4 == NULL) );
    assert( tmp_import_from_1__module == NULL );
    Py_INCREF( tmp_assign_source_4 );
    tmp_import_from_1__module = tmp_assign_source_4;

    // Frame without reuse.
    frame_7e5c1f9ebdac02e5fbab2b23ff460504 = MAKE_MODULE_FRAME( codeobj_7e5c1f9ebdac02e5fbab2b23ff460504, module_numpy$lib$info );

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStack( frame_7e5c1f9ebdac02e5fbab2b23ff460504 );
    assert( Py_REFCNT( frame_7e5c1f9ebdac02e5fbab2b23ff460504 ) == 2 );

    // Framed code:
    // Tried code:
    tmp_import_name_from_1 = tmp_import_from_1__module;

    CHECK_OBJECT( tmp_import_name_from_1 );
    tmp_assign_source_5 = IMPORT_NAME( tmp_import_name_from_1, const_str_plain_division );
    if ( tmp_assign_source_5 == NULL )
    {
        assert( ERROR_OCCURRED() );

        FETCH_ERROR_OCCURRED( &exception_type, &exception_value, &exception_tb );


        exception_lineno = 157;

        goto try_except_handler_1;
    }
    UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain_division, tmp_assign_source_5 );
    tmp_import_name_from_2 = tmp_import_from_1__module;

    CHECK_OBJECT( tmp_import_name_from_2 );
    tmp_assign_source_6 = IMPORT_NAME( tmp_import_name_from_2, const_str_plain_absolute_import );
    if ( tmp_assign_source_6 == NULL )
    {
        assert( ERROR_OCCURRED() );

        FETCH_ERROR_OCCURRED( &exception_type, &exception_value, &exception_tb );


        exception_lineno = 157;

        goto try_except_handler_1;
    }
    UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain_absolute_import, tmp_assign_source_6 );
    tmp_import_name_from_3 = tmp_import_from_1__module;

    CHECK_OBJECT( tmp_import_name_from_3 );
    tmp_assign_source_7 = IMPORT_NAME( tmp_import_name_from_3, const_str_plain_print_function );
    if ( tmp_assign_source_7 == NULL )
    {
        assert( ERROR_OCCURRED() );

        FETCH_ERROR_OCCURRED( &exception_type, &exception_value, &exception_tb );


        exception_lineno = 157;

        goto try_except_handler_1;
    }
    UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain_print_function, tmp_assign_source_7 );
    goto try_end_1;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_type_1 = exception_type;
    exception_keeper_value_1 = exception_value;
    exception_keeper_tb_1 = exception_tb;
    exception_keeper_lineno_1 = exception_lineno;
    exception_type = NULL;
    exception_value = NULL;
    exception_tb = NULL;
    exception_lineno = 0;

    CHECK_OBJECT( (PyObject *)tmp_import_from_1__module );
    Py_DECREF( tmp_import_from_1__module );
    tmp_import_from_1__module = NULL;

    // Re-raise.
    exception_type = exception_keeper_type_1;
    exception_value = exception_keeper_value_1;
    exception_tb = exception_keeper_tb_1;
    exception_lineno = exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;

    // Restore frame exception if necessary.
#if 0
    RESTORE_FRAME_EXCEPTION( frame_7e5c1f9ebdac02e5fbab2b23ff460504 );
#endif
    popFrameStack();

    assertFrameObject( frame_7e5c1f9ebdac02e5fbab2b23ff460504 );

    goto frame_no_exception_1;
    frame_exception_exit_1:;
#if 0
    RESTORE_FRAME_EXCEPTION( frame_7e5c1f9ebdac02e5fbab2b23ff460504 );
#endif

    if ( exception_tb == NULL )
    {
        exception_tb = MAKE_TRACEBACK( frame_7e5c1f9ebdac02e5fbab2b23ff460504, exception_lineno );
    }
    else if ( exception_tb->tb_frame != &frame_7e5c1f9ebdac02e5fbab2b23ff460504->m_frame )
    {
        exception_tb = ADD_TRACEBACK( exception_tb, frame_7e5c1f9ebdac02e5fbab2b23ff460504, exception_lineno );
    }

    // Put the previous frame back on top.
    popFrameStack();

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    CHECK_OBJECT( (PyObject *)tmp_import_from_1__module );
    Py_DECREF( tmp_import_from_1__module );
    tmp_import_from_1__module = NULL;

    tmp_assign_source_8 = LIST_COPY( const_list_str_plain_core_str_plain_testing_list );
    UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain_depends, tmp_assign_source_8 );
    tmp_assign_source_9 = LIST_COPY( const_list_str_chr_42_list );
    UPDATE_STRING_DICT1( moduledict_numpy$lib$info, (Nuitka_StringObject *)const_str_plain_global_symbols, tmp_assign_source_9 );

    return MOD_RETURN_VALUE( module_numpy$lib$info );
    module_exception_exit:
    RESTORE_ERROR_OCCURRED( exception_type, exception_value, exception_tb );
    return MOD_RETURN_VALUE( NULL );
}

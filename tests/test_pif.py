import unittest
from dfttopif import directory_to_pif, convert
from pypif_sdk.accessor import get_propety_by_name
import tarfile
import os
import shutil
import glob


def delete_example(name):
    '''Delete example files that were unpacked
    using the `unpack_example(path)` function
    
    Input:
        name - Name of example file
    '''
    shutil.rmtree(name)


def unpack_example(path):
    '''Unpack a test case to a temporary directory
    
    Input:
        path - String, path to tar.gz file containing
            a certain test case
    '''
    
    # Open the tar file
    tp = tarfile.open(path)
    
    # Extract to cwd
    tp.extractall()


class TestPifGenerator(unittest.TestCase):
    '''
    Tests for the tool that generates the pif objects
    '''
    
    def test_VASP(self):
        '''
        Test ability to parse VASP directories
        '''
        
        test_quality_report = True
        for file in glob.glob(os.path.join('examples','vasp','*.tar.gz')):
            # Get the example files
            unpack_example(file)
            name = ".".join(os.path.basename(file).split(".")[:-2])
            
            # Make the pif file
            # print("\tpif for example:", name)
            result = directory_to_pif(name, quality_report=test_quality_report)
            # Only hit the quality report endpoint once to avoid load spikes in automated tests
            test_quality_report=False
            self.assertIsNotNone(result.chemical_formula)
            self.assertIsNotNone(result.properties)
            # print(pif.dumps(result, indent=4))
            
            # Delete files
            delete_example(name)

        # Test if we only have a single OUTCAR
        unpack_example(os.path.join('examples', 'vasp', 'AlNi_static_LDA.tar.gz'))

        #  First, try to constrain what the parser is allowed to read
        result = convert([os.path.join('AlNi_static_LDA', 'OUTCAR')])
        self.assertTrue(get_propety_by_name(result, "Converged").scalars[0].value)
        self.assertIsNone(get_propety_by_name(result, "Band Gap Energy"))  # No access to DOSCAR

        #  Remove all files but OUTCAR
        for f in os.listdir('AlNi_static_LDA'):
            if f != 'OUTCAR':
                os.unlink(os.path.join('AlNi_static_LDA', f))

        #   Run the conversion, check that it returns some data
        result = convert([os.path.join('AlNi_static_LDA', 'OUTCAR')])
        self.assertTrue(get_propety_by_name(result, "Converged").scalars[0].value)

        # Try parsing if we have two OUTCARs
        shutil.copy(os.path.join('AlNi_static_LDA', 'OUTCAR'), os.path.join('AlNi_static_LDA', 'OUTCAR.2'))

        #   Make sure it only parsers the first
        result = convert([os.path.join('AlNi_static_LDA', 'OUTCAR')])
        self.assertTrue(get_propety_by_name(result, "Converged").scalars[0].value)

        delete_example('AlNi_static_LDA')

    def test_PWSCF(self):
        '''
        Test ability to parse PWSCF directories
        '''
        
        for file in glob.glob(os.path.join('examples','pwscf','*.tar.gz')):
            # Get the example files
            unpack_example(file)
            name = ".".join(os.path.basename(file).split(".")[:-2])
            
            # Make the pif file
            # print("\tpif for example:", name)
            try:
                result = directory_to_pif(name)
            except Exception as e:
                print('Failure for {}'.format(name))
                raise e
            assert result.chemical_formula is not None
            assert result.properties is not None
            # print(pif.dumps(result, indent=4))
            
            # Delete files
            delete_example(name)
        
if __name__ == '__main__':
    unittest.main()

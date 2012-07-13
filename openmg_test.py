import numpy as np
from openmg import *
from sys import _getframe
from pyamg.gallery import poisson as poissonpyamg  # I should write my own.


def tests():
    '''
    This is the only function that actually gets executed when this file is
    run as __main__. Put tests in here to run them easily.
    '''
#    test_123d_noise_mg()  # this is a good one
#    test_gs_thresh()
#    test_a()
#    test_b()
#    test_c()
#    test_d()
    test_3d_noise_mg_multi_N()
#    test_1d_noise_mg()
#    test_2d_noise_mg()
#    test_3d_noise_mg()
#    test_2d_mpl_demo()
#    test_1d_multifreq(18000,4)
    pass


def whoami(level=1):
    '''Return the name of the calling function. Specifying a level greater than
    1 will return the name of the calling function's caller.'''
    return _getframe(level).f_code.co_name


def saytest():
    '''Declare that a test is beginning!'''
    print ''
    print 'TEST >>>>', whoami(2)


def test_a():
    '''
    Poisson equation on a sine curve. In 3D?
    It wasn't originally, but the restriciton algorithm was having
    trouble with 1D. This might bear investigation.
    '''
    saytest()
    iterations = 5
    problemscale = 12
    size = problemscale ** 3
    gridlevels = 2
    u_zeros = np.zeros((size,))
    u_actual = np.sin(np.array(range(int(size))) * 3.0 / size).T
    A = poissonpyamg((size,))
    #print u_actual
    #print A
    #print "A (shape %s) is:" % (A.shape,)
    #print A
    #print "u_actual is %s." % u_actual
    b = flexible_mmult(A, u_actual)
    #print "b is %s." % b
    u_iterative = iterative_solve(A, b, u_zeros, iterations)
    #u_slow=slow_iterative_solve(A,b,b,10)
    parameters = {'coarsest_level': gridlevels - 1,
                  'problemshape': (problemscale, problemscale, problemscale),
                  'gridlevels': gridlevels,
                  'iterations': iterations,
                  'verbose': True, }
    u_mmg = mg_solve(A, b, parameters)[0]
    make_graph("actual.png", "actual at n=%s" % size, u_actual)
    make_graph("iterative.png", "iterative at n=%s" % size, u_iterative)
    make_graph("multigrid.png", "mmg at n=%s" % size, u_mmg)
    print sparse.base.np.linalg.norm(b - flexible_mmult(
                                                A,
                                                u_iterative.reshape((size, 1))
                                              )
                                         )


def test_b():
    '''Demonstrate the restriction matrix generator.
    '''
    saytest()
    N = 4096
    shape = (16, 16, 16,)
    print 'for N = %i' % N, 'restriction matrix has shape',\
                             restriction(N, shape).shape


def test_c():
    '''Run the test_1d_multifreq test with four different N arguments'''
#    thousands = [10, 30, ]
    thousands = [1, 3, ]
    frames = 5  # output gets compiled into a movie!
    multifreq_Ns = map(lambda x: int(x * 10 ** 3), thousands)
    for N in multifreq_Ns:
        test_1d_multifreq(N, frames)


def test_d():
    '''Run the test_2d_multifreq test with four different N arguments'''
#    thousands = [10,30,]
    tens = [1, 2]
    frames = 5  # output gets compiled into a movie!
#    multifreq_problemscales = map(lambda x: int(x * 10 ** 3), thousands)
    multifreq_problemscales = map(lambda x: int(x * 10 ** 1), tens)
    for NX in multifreq_problemscales:
        test_2d_multifreq(NX, frames)


def test_1d_multifreq(N, finaliterations, spectralxscale='linear', solutionname='whitenoise'):
    '''Generates 1-dimensional uniform noise with N unknowns, then applies
    Gauss-Siedel smoothing iterations to an initial zero-vector guess until
    finaliterations is reached, graphing the Fourier transform of the error
    each time. Does so pretty inefficiently, by doing 1 iteration, 2 iterations,
    3, iterations, etc. until finaliterations, instead of just doing
    finaliterations iterations, and graphing after each sweep.'''
    saytest()
    print 'N is', N
    import matplotlib.pyplot as plt
    from scipy import fftpack
    from os import system
    if solutionname == 'summedsine':  # Summed sine waves of several frequencies.
        data = np.zeros((N,))  # initialize
        domainwidthsexponents = range(10)
        domainwidths = range(10)  # initialize
        for i in range(10):
            domainwidths[i] = float(N) / (2.0 ** domainwidthsexponents[i])
        for domainwidth in domainwidths:
            sininput = np.arange(0.0, domainwidth, domainwidth / N)
            xdata = (np.sin(sininput) / domainwidth * 10.0)[0:N:]
            data = data + xdata
    else:
        solutionname = 'whitenoise'
        data = np.random.random((N,))  # 1D white noise
    gif_output_name = 'spectral_solution_rate-%i_unknowns-%s_xscale-%s_solution.gif' % (N, spectralxscale, solutionname)
    print gif_output_name

    A = poissonpyamg((N,))
    b = flexible_mmult(A, data)

#    Prepare for Graphing
    fig = plt.figure(figsize=(7.5, 7))
    fig.suptitle(gif_output_name)
    fig.subplots_adjust(wspace=.2)
    fig.subplots_adjust(hspace=.2)
    solnax = fig.add_subplot(211)  # subplot to hold the solution
    solnaxylim = [0, 1]
    specax = fig.add_subplot(212)  # subplot to hold the spectrum
    specaxylim = [10.0 ** (-18), 10.0 ** 3]

    solutions = []
    spectra = []
    filenames = []
    loop = 1  # for monitoring progress

    iterationslist = range(finaliterations)
#    from random import shuffle
#    shuffle(iterationslist)
    iterations_to_save = range(1, finaliterations + 1)
    str_tosave = []
    for x in iterations_to_save:
        str_tosave.append(str(x))
    csvfilelabel = 'iterative_spectra-%i_N' % N
    csvfile = open('output/%s.csv' % csvfilelabel, 'a')
    csvfile.write('frequency,' + ','.join(str_tosave) + '\n')
    csvfile.flush()
    for iterations in iterationslist:
        solutions.append(iterative_solve(A,
                                         b,
                                         np.zeros((N,)),
                                         iterations,
                                         verbose=verbose)
                                        )
        spectra.append(fftpack.fft(b - flexible_mmult(A,
                                                      solutions[iterations]
                                                     )
                                  )
                      )
        filebasename = '%i_unknowns-%i_iterations' % (N, iterations)
        filename = filebasename + '-solution.png'
        solnax.set_ylim(solnaxylim)
        solnax.set_autoscaley_on(False)
        solnax.set_title(filebasename + ': Solution')
        solnax.plot(solutions[iterations])

        specax.set_yscale('log')
        specax.set_xscale(spectralxscale)
        specax.set_ylim(specaxylim)
        specax.set_autoscaley_on(False)
        specax.set_title(filebasename + ': Solution Error (frequency domain)')
        specax.plot(spectra[iterations])

        filename = 'temp/' + filebasename + '-combined.png'
        filenames.append(filename)
        print "%i of %i: " % (loop, finaliterations) + "saving " + filename
        fig.savefig(filename, dpi=80)
        solnax.cla()
        specax.cla()
        loop += 1
    frequencies = range(len(solutions[0]))
    for i in frequencies:
        towrite = '%i,' % frequencies[i]
        for spectrum in spectra:
            towrite += '%.8f,' % abs(spectrum[i])
        csvfile.write(towrite + '\n')
        csvfile.flush()
    csvfile.close()

    # make .gif and .mp4 files:
    torun=range(9)
    torun[1] = 'convert ' + ' '.join(filenames) + ' output/%s' % gif_output_name
    torun[2] = 'rm ' + ' '.join(filenames)
    torun[3] = 'cp %s simple.gif' % ('output/' + gif_output_name)
    torun[4] = 'mplayer -vo jpeg simple.gif'
    torun[5] = 'ffmpeg -r 12 -i %%08d.jpg -y -an output/%s.avi 1> /dev/null' % gif_output_name
    torun[6] = 'rm simple.gif 0*.jpg'
    torun[7] = 'ffmpeg -y -i output/%s.avi output/%s.mp4 && rm output/%s.avi' % (gif_output_name, gif_output_name, gif_output_name)
    system(torun[1])
    system(torun[2])
    system(torun[3])
    system(torun[4])
    system(torun[5])
    system(torun[6])
    system(torun[7])

def test_2d_multifreq(problemscale,finaliterations):
    '''Attempts to generate a pretty 2D solution, by summing several 2D
    sine waves of different frequencies. Then, proceeds to apply a GS smoother
    to the generated problem, saving pretty pictures after each iteration.
    This might work OK if problemscale is big enough.
    '''
    saytest()
    import matplotlib.pyplot as plt
    from scipy import fftpack
    from matplotlib import cm
    from mpl_toolkits.mplot3d import Axes3D

    # Generate test problem. Summed sine waves of several resolutions:
    NX = problemscale
    floatNX = float(NX)
    data = np.zeros((NX, NX))
    domainwidths = [floatNX, floatNX / 2.0, 10., 3.1415]
    for domainwidth in domainwidths:
        sininput = np.arange(0.0, domainwidth, domainwidth / NX)
        xdata = (np.sin(sininput) / domainwidth * 10.0)[0:NX:]
        data = data + xdata[:, np.newaxis] + xdata[:, np.newaxis].T
    X = np.tile(np.array(range(NX)), (NX, 1))
    Y = X.T

    # Prepare for Graphing:
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_zlim3d([-1, 6])
    specfig = plt.figure()
    specax = specfig.add_subplot(111)
    specax.set_ylim([.000001, 10000])
    specax.set_autoscaley_on(False)
    specax.set_xscale('log')

    # Problem Setup:
    A = poissonpyamg((NX, NX))
    solnforb = data.ravel().reshape((NX ** 2, 1))
    b = flexible_mmult(A, solnforb)

    # Initial "Solution" placeholder:
    solutions = range(finaliterations)
    spectra = range(finaliterations)
    iterations = 0
    solutions[iterations] = np.zeros((NX, NX)).ravel()
    spectra[iterations] = b - flexible_mmult(A, solutions[iterations])

    # Initial graphs:
    print "%i iterations" % iterations
    filebasename = 'output/N_%i-iterations_%i' % (NX ** 2, iterations)
    filename = filebasename + '.png'
    ax.set_title(filebasename)
    #surf = ax.plot_wireframe(X, Y, solutions[iterations].reshape(NX,NX),rstride=stridelength,cstride=stridelength)
    surf = ax.plot_surface(X, Y, data, cmap=cm.jet)
    print "saving", filename
    fig.savefig(filename)
    surf.remove()
    ax.cla()

    # Error Spectrum
    specax.plot(spectra[iterations])
    specax.set_title(filebasename + ': Error Spectrum')
    filename = filebasename + '-error.png'
    specfig.savefig(filename)
    del specax.lines[0]
    specax.cla()

    for iterations in range(1, finaliterations):
        solutions[iterations] = iterative_solve(A,
                                                b,
                                                np.zeros(NX ** 2),
                                                iterations,
                                                verbose=verbose
                                               ).reshape(NX, NX)
        spectra[iterations] = fftpack.fft2(solutions[iterations])

        filebasename = 'output/N_%i-iterations_%i' % (NX ** 2, iterations)
        filename = filebasename + '-solution.png'
        ax.set_zlim3d([-1, 6])
        surf = ax.plot_surface(X, Y, solutions[iterations], cmap=cm.jet)
        ax.set_title(filebasename)
        surf = ax.plot_wireframe(X, Y, solutions[iterations])
        print "saving", filename
        fig.savefig(filename)
        surf.remove()
        ax.cla()

        specax.set_yscale('log')
        specax.set_ylim([.000001, 10000])
        specax.set_autoscaley_on(False)
        specax.set_xscale('log')
        specax.plot(spectra[iterations])
        specax.set_title(filebasename + ': Error Spectrum')
        filename = filebasename + '-error.png'
        print "saving", filename
        specfig.savefig(filename)
        del specax.lines[0]
        specax.cla()

def test_gs_thresh():
    '''Test the Gauss-Siedel to-threshold solver.'''
    saytest()
    NX = 12
    NY = NX
    N = NX * NY
    A = poisson2d((NX, NY,))
    b = np.random.random((N,))
    x_init = np.zeros((N,))
    threshold = 0.0001
    verbose = True
    (x, info_dict) = iterative_solve_to_threshold(A, b, x_init,
                                                threshold,
                                                verbose=verbose)
    print 'norm is ', (np.linalg.norm(getresidual(b, A, x, N)))


def test_1d_noise_mg():
    '''Solve a 2D Poisson equation, with the solution being 2D white noise,
    i.e., np.random.random((NX,NY)). Useful as a sanity check.
    '''
    NX = 512
    N = NX
    u_actual = np.random.random((NX,)).reshape((N, 1))
    A_in = poissonpyamg((NX,))
    b = flexible_mmult(A_in, u_actual)
    (u_mg, info_dict) = mg_solve(A_in, b, {
                                           'problemshape': (NX,),
                                           'gridlevels': 3,
                                           'iterations': 1,
                                           'verbose': True,
                                           'threshold': 4
                                          }
                                )
    print 'test_1d_noise_mg: final norm is ', info_dict['norm']


def test_2d_noise_mg():
    '''
    Solve a 2D Poisson equation, with the solution being 2D white noise, i.e.,
    np.random.random((NX,NY)). Useful as a sanity check.
    '''
    NX = 32
    NY = NX
    N = NX * NY
    u_actual = np.random.random((NX, NY)).reshape((N, 1))
    A_in = poissonpyamg((NX, NY))
    b = flexible_mmult(A_in, u_actual)
    (u_mg, info_dict) = mg_solve(A_in, b, {
                                           'problemshape': (NX, NY),
                                           'gridlevels': 3,
                                           'iterations': 1,
                                           'verbose': True,
                                           'threshold': 4
                                          }
                                )
    print 'test_2d_noise_mg: final norm is ', info_dict['norm']


def test_3d_noise_mg():
    '''
    Solve a 3D Poisson equation, with the solution being 3D white noise, i.e.,
    np.random.random((NX,NY,NZ)). Useful as a sanity check.
    '''
    NX = 12
    NY = NZ = NX
    N = NX * NY * NZ
    u_actual = np.random.random((NX, NY, NZ)).reshape((N, 1))
    A_in = poissonpyamg((NX, NY, NZ))
    b = flexible_mmult(A_in, u_actual)
    (u_mg, info_dict) = mg_solve(A_in, b, {
                                           'problemshape': (NX, NY, NZ),
                                           'gridlevels': 3,
                                           'iterations': 1,
                                           'verbose': True,
                                           'threshold': 4
                                          }
                                )
    print 'test_3d_noise_mg: final norm is ', info_dict['norm']


def test_123d_noise_mg():
    '''Combo OpenMG test of 1D, 2D, and 3D.'''
    saytest()
    test_1d_noise_mg()
    test_2d_noise_mg()
    test_3d_noise_mg()


def test_3d_noise_mg_multi_N():
    '''
    Solve a 3D Poisson equation, with the solution being 3D white noise, i.e.,
    np.random.random((NX,NY,NZ)). Useful as a sanity check, and as a check
    on what is the allowable maximum problemsize with your memory.
    '''
    saytest()
    NXes = range(1, 16)
#    NXes = range(8, 16)[::4]
#    NXes = range(8, 22)[::2]
#    NXes = range(8, 22)[::4]
    print ''
    for NX in NXes:
        try:
            NY = NZ = NX
            N = NX * NY * NZ
            print 'NX is', NX, 'and N is ', N, ':'
            u_actual = np.random.random((NX, NY, NZ)).reshape((N, 1))
            A_in = poissonpyamg((NX, NY, NZ))
            b = flexible_mmult(A_in, u_actual)
            (u_mg, info_dict) = mg_solve(A_in, b,
                                {'problemshape': (NX, NY, NZ),
                                 'gridlevels': 3,
                                 'iterations': 1,
                                 'verbose': False,
                                 'threshold': .0001
                                })
            print '    test_3d_noise_mg:', info_dict
        except:
            errortext = sys.exc_info()[0]
            print '    ERROR:', errortext
        print ''


def test_2d_mpl_demo():
    '''
    Plot a pretty 2D surface, and the result of solving a 2D Poisson equation
    with that surface as the solution.
    '''
    saytest()
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    sizemultiplier = 4
    NX = 8 * sizemultiplier
    cycles = 3
    actualtraces = 8
    mgtraces = 16
    NY = NX
    N = NX * NY
    (X, Y, u_actual) = mpl_test_data(delta=1 / float(sizemultiplier))
    A_in = poissonpyamg((NX, NY))
    b = flexible_mmult(A_in, u_actual.ravel())
    u_mg = mg_solve(A_in, b, {
                              'problemshape': (NX, NY),
                              'gridlevels': 2,
                              'iterations': 1,
                              'verbose': True,
                              'cycles': 300,
                              'dense': True
                             }
                   )

    fig = plt.figure()
    ax = Axes3D(fig)
    fig.suptitle('blue is actual; red is %i v-cycles; %i unknowns' % (cycles, N))
    #ax = fig.add_subplot(111,projection='3d') #not in matplotlib version 0.99, only version 1.x
    ax.plot_wireframe(X, Y, u_actual,
                      rstride=NX / actualtraces,
                      cstride=NY / actualtraces,
                      color=((0, 0, 1.0),)
                     )
    #ax.scatter(X,Y,u_mg[0],c=((1.,0,0),),s=40)
    ax.plot_wireframe(X, Y, u_mg[0].reshape((NX,NY)),
                      rstride=NX / mgtraces,
                      cstride=NY / mgtraces,
                      color=((1.0,0,0),)
                     )
    filename = 'output/test_2d_mpl_demo-%i_vycles-%i_N.png' % (cycles, N)
    fig.savefig(filename)
    #plt.show()
    print 'u_mg[0] is', u_mg[0]


def mpl_test_data(delta=0.25):
    '''
    Return a tuple X, Y, Z with a test data set.
    Modified from matplotlib's mpl_toolkits.mplot3d.axes3d.get_test_data
    '''
    saytest()
    from matplotlib.mlab import  bivariate_normal
    x = y = np.arange(-4.0, 4.0, delta)
    X, Y = np.meshgrid(x, y)

    Z1 = bivariate_normal(X, Y, 1.0, 1.0, 0.0, 0.0)
    Z2 = bivariate_normal(X, Y, 1.5, 0.5, 1, 1)
    Z = Z2 - Z1

    X = X * 16
    Y = Y * 16
    Z = Z * 512
    return X, Y, Z


def do_error():
    '''Call this if you want to force an error at a particular place.'''
    a_dictionary = {'one': 1}
    x = a_dictionary['two']
    return x  # obviously, we'll never get here.


if __name__ == "__main__":
    tests()

/* 2021 - 2023 Jan Provaznik (jan@provaznik.pro)
 *
 * Do you know that feeling when you spend an exorbitant amount of time
 * building a better alternative only to end up with a considerably worse
 * result hindered by fundamental limitations?
 *
 * I, for one, believe I do now. Anyway.
 */

#include <memory>
#include <vector>
#include <string>

#include <Nomad/nomad.hpp>
#include <Algos/EvcInterface.hpp>
#include <Cache/CacheBase.hpp>

#include <boost/python.hpp>
#include <boost/python/numpy.hpp>

namespace bpy = boost::python;
namespace bnp = boost::python::numpy;

// Aliases for NOMAD (related) types.

using nomad_eval_block_t = NOMAD::Block;
using nomad_eval_point_t = NOMAD::EvalPoint;
using nomad_eval_float_t = NOMAD::Double;
using nomad_eval_state_t = std::vector<bool>;
using nomad_eval_param_t = std::shared_ptr<NOMAD::EvalParameters>;

// Forward declarations
//

struct proxy_block_evaluator;

// NOMAD::EvalPoint conversion

bnp::ndarray 
make_ndarray_from_point (
  const nomad_eval_point_t & point);

// NOMAD::Block conversion

bpy::list 
make_ndarray_list_from_block (
  const nomad_eval_block_t & block, 
  size_t bsize);

// NOMAD::EvalPoint evaluation data (objective, point) conversion

bpy::object 
make_solution_from_point (
  const nomad_eval_point_t & point);

// NOMAD::EvalPoint evaluation data (objective, point) extraction

bpy::object 
make_optimal_solution_only (
  const std::vector<nomad_eval_point_t> & points);

bpy::list 
make_optimal_solution_list (
  const std::vector<nomad_eval_point_t> & points);

// Utility: Convert NOMAD::EvalPoint into numpy.ndarray vector.

bnp::ndarray 
make_ndarray_from_point (
  const nomad_eval_point_t & point
) {
  // Honestly the interface of NOMAD::EvalPoint, 
  // resp. that of NOMAD::ArrayOfDouble, leaves a terrible after taste.

  size_t psize = point.size();

  // Allocate empty boost::python::numpy::ndarray in the right shape and type.

  auto shape = bpy::make_tuple(psize);
  auto dtype = bnp::dtype::get_builtin<double>();
  auto array = bnp::empty(shape, dtype);

  // We must extract the actual value (double) from each 
  // NOMAD::Double component of NOMAD::ArrayOfDouble.
  // 
  // Yes, you have guessed it, NOMAD::Double wraps the actual 'double' which
  // makes it impossible to initialize the boost::python::numpy::ndarray
  // instance with contiguous memory.

  for (size_t index = 0; index < psize; ++index) {
    array[index] = point[index].todouble();
  }

  return array;
}

// Utility: Convert the NOMAD::Block into a list of numpy.ndarray vectors 
// representing individual instances of NOMAD::EvalPoint within the block.

bpy::list 
make_ndarray_list_from_block (
  const nomad_eval_block_t & block, 
  size_t bsize
) {
  bpy::list list;
  for (size_t index = 0; index < bsize; ++index) {
    auto array = make_ndarray_from_point(* block[index]);
    list.append(array);
  }
  return list;
}

// Utility: Convert NOMAD::Point into a (result, array) tuple.

bpy::object 
make_solution_from_point (
  const nomad_eval_point_t & point
) {
  auto value = point.getEval(NOMAD::EvalType::BB)->getF().todouble();
  auto array = make_ndarray_from_point(point);
  return bpy::make_tuple(value, array);
}

// Utility: Given a list of NOMAD::Point instances,
// convert the first point into the solution tuple.
// 
// Return None (represented by empty boost::python::object) if list empty.

bpy::object 
make_optimal_solution_only (
  const std::vector<nomad_eval_point_t> & points
) {
  if (points.empty())
    return bpy::object();
  return make_solution_from_point(points.front());
}

// Utility: Given a list of NOMAD::Point instances,
// convert every point into a list of solution tuples.

bpy::list 
make_optimal_solution_list (
  const std::vector<nomad_eval_point_t> & points
) {
  bpy::list list;
  for (const auto & point : points) {
    auto solution = make_solution_from_point(point);
    list.append(solution);
  }
  return list;
}

// Heavy lifting.
//
// The NOMAD solver evaluated the blackbox by repeatedly calling eval_block.
// This function then passes the requested points of interest to the Python 
// callback which returns the corresponding blackbox output.

struct proxy_block_evaluator : public NOMAD::Evaluator {

  proxy_block_evaluator (bpy::object callback, const nomad_eval_param_t & params) : 
    NOMAD::Evaluator(params, NOMAD::EvalType::BB), $callback(callback) {
  }

  virtual ~ proxy_block_evaluator () {
  }

  // As per https://github.com/bbopt/nomad/blob/master/src/Eval/EvalPoint.hpp
  // NOMAD::Block aliases std::vector<std::shared_ptr<NOMAD::EvalPoint>>
  //
  // The basic idea would be to create a list of numpy.ndarray vectors 
  // representing the points.

  nomad_eval_state_t 
  eval_block (
    nomad_eval_block_t & block, 
    const nomad_eval_float_t & hmax, 
    nomad_eval_state_t & include
  ) const override {

    size_t bsize = block.size();

    // Nomad::Evaluator::eval_block returns a list of indicators 
    // whether the individual evaluations were successful.

    nomad_eval_state_t success(bsize);

    // Nomad::Evaluator::eval_block modifies a list of indicators 
    // whether the individual evaluations are to be included in optimization.

    include.resize(bsize);

    // Construct a python-friendly payload of evaluation points represented
    // using numpy.ndarray vectors.

    bpy::list payload = make_ndarray_list_from_block(block, bsize);

    // Invoke the callback python-function.
    //
    // It is passed a list of numpy.ndarray points to evaluate the blackbox at.
    // It is expected to return an iterable over (success, include, outcome)
    // triplets respective to the individual blackbox evaluations.

    bpy::object gen = $callback(payload);

    // Process the returned iterable.
    //
    // We expect that the triplets (success, include, outcome) satisfy the
    // following requirements...
    //
    // (1) success is boolean-convertible (bool, int),
    // (2) include is boolean-convertible (bool, int),
    // (3) outcome is std::string-convertible (str).

    auto cur = bpy::stl_input_iterator<bpy::tuple>(gen);
    auto end = bpy::stl_input_iterator<bpy::tuple>();

    for (size_t index = 0; cur != end && index < bsize; ++cur, ++index) {

      bpy::tuple element = (* cur);

      auto extract_success = bpy::extract<bool>(element[0]);
      auto extract_include = bpy::extract<bool>(element[1]);
      auto extract_outcome = bpy::extract<std::string>(element[2]);

      if (! extract_success.check())
        throw std::runtime_error("Could not convert 'success' indicator to bool.");
      if (! extract_include.check())
        throw std::runtime_error("Could not convert 'include' indicator to bool.");
      if (! extract_outcome.check())
        throw std::runtime_error("Could not convert 'outcome' indicator to string.");

      // Save the particular values into appropriate Nomad structures.

      include[index] = extract_include();
      success[index] = extract_success();

      // Please note that it is up to the user to ensure the string
      // adheres to the user-defined BB_OUTPUT_TYPE structure.

      block[index]->setBBO(extract_outcome());
    }

    return success;
  }

  private:
    bpy::object $callback;
};

// Wrapper: Python interface for the optimization engine. 
//
//  (1) evaluator must be a callable
//
//      It is repeatedly called by NOMAD. A list of numpy.ndarray points is
//      passed in each call, the function must evaluate the blackbox there.
//
//      It must return an iterable over (success, include, outcome) tuples
//      corresponding to individual blackbox evaluations. Elements of the
//      iterable must follow the same order as the input points.
//
//      (1.1) success must be boolean-convertible and determines whether the
//            evaluation was successful
//      (1.2) include must be boolean-convertible and indicates whether NOMAD
//            should actually include the evaluation in its search
//      (1.3) outcome must be a string conforming to the BB_OUTPUT_TYPE option
//
//  (2) params must be a list of strings
//
//      It is used to initialize NOMAD software.
//      Notable parameters include X0, LOWER_BOUND, UPPER_BOUND, BB_OUTPUT_TYPE,
//      BB_MAX_BLOCK_SIZE, and MAX_BB_EVAL.
//
//  (3) multiple must be boolean-convertible 
//
//      Ir determines whether multiple equally good solutions should be returned,
//      defaults to false: only the first best solution is returned.
//
//  Returns a tuple (termination_success, eval_count, best_feasible, best_infeasible).
//
//  (1) termination_success determines the exit condition of the solver
//  (2) eval_count determines the number of blackbox evaluations
//  (3) best_feasible is either (best_value, best_point) tuple (if multiple = 0),
//      a list of these tuples (if multiple = 1) or None if there was no feasible
//      solution found.
//  (4) best_infeasible behaves like best_feasible

bpy::object 
nomad_minimize_wrapper (
  bpy::object callback, 
  bpy::object options, 
  bool multiple
) {

  // Configuration of the optimizer engine.
  //

  // The handling of NOMAD parameters has changed in version 4.3 of NOMAD. It
  // is now necessary to validate parameters after readParamLine calls.
  //
  // https://github.com/bbopt/nomad/issues/110

  auto params = std::make_shared<NOMAD::AllParameters>();

  auto optcur = bpy::stl_input_iterator<std::string>(options);
  auto optend = bpy::stl_input_iterator<std::string>();

  for (; optcur != optend; ++optcur) {
    params->readParamLine(* optcur);
  }

  // Apparently boost::python does not bode well in multi-threaded environment.
  //
  // Nomad can be instructed (via NB_THREADS_OPENMP) to utilize a number of
  // threads during the evaluation of candidate points.
  //
  // We explicitly set the parameter to enforce evaluation in a single thread.

  params->readParamLine("NB_THREADS_OPENMP 1");

  // Parameters have to be checked. 
  // @todo We just re-throw the exception if it happens. 

  try {
    params->checkAndComply();
  }
  catch (...) {
    throw;
  }

  // Blackbox block-evaluator
  auto evalopt = params->getEvalParams();
  auto evalfun = std::make_shared<proxy_block_evaluator>(callback, evalopt);

  // The optimization engine Nomad::MainStep
  auto engine = std::make_unique<NOMAD::MainStep>();

  // ... is given the parameters and the blackbox evaluator.
  engine->setAllParameters(params);
  engine->setEvaluator(evalfun);

  // Begin the optimization process.
  
  bool engine_termination_success = false;

  try {
    engine->start();
    engine_termination_success = engine->run();
    engine->end();
  }
  catch (...) {
    throw;
  }

  // Collect the information to report on the optimization.
  //
  // - engine termination success
  // - engine termination status
  // - blackbox evaluation count
  // - optimal   feasible (value, point)
  // - optimal infeasible (value, point)

  int engine_termination_status = engine->getRunFlag();

  // After consulting the documentation and the implementation of 
  // the C interface I guess this is the only way to retrieve the 
  // results of the optimization.
  
  size_t best_feasible_count, best_infeasible_count;
  std::vector<nomad_eval_point_t> best_feasible_list, best_infeasible_list;

  // The NOMAD::CacheBase holds information about each and every blackbox
  // evaluation. We can ask it to find the best (in)feasible evaluation.

  best_feasible_count = NOMAD::CacheBase::getInstance()->findBestFeas(best_feasible_list, 
    NOMAD::Point(), NOMAD::EvalType::BB, NOMAD::ComputeType::STANDARD);

  best_infeasible_count = NOMAD::CacheBase::getInstance()->findBestInf (best_infeasible_list, NOMAD::INF,
    NOMAD::Point(), NOMAD::EvalType::BB, NOMAD::ComputeType::STANDARD);

  // There can be multiple equally good values.
  // We return them all at the user's behest.

  bpy::object best_feasible_solution;

  if (best_feasible_count) {
    best_feasible_solution = multiple ?
      make_optimal_solution_list(best_feasible_list) :
      make_optimal_solution_only(best_feasible_list);
  }

  bpy::object best_infeasible_solution;

  if (best_infeasible_count) {
    best_infeasible_solution = multiple ?
      make_optimal_solution_list(best_infeasible_list) :
      make_optimal_solution_only(best_infeasible_list);
  }

  // Determine the number of evaluations.
  //
  // For whichever reason, using
  // NOMAD::EvcInterface::getEvaluatorControl()->getBbEval();
  // does not work and returns garbage.
  //
  // Using the number of points in Cache content instead. 
  // Might be less precise.

  size_t eval_count = NOMAD::CacheBase::getInstance()->size();

  // Ensure we are using Nomad with a clean slate on the next run.

  NOMAD::OutputQueue::Flush();
  NOMAD::CacheBase::getInstance()->clear();
  NOMAD::MainStep::resetComponentsBetweenOptimization();

  // Report on the optimization.
  //
  // - engine termination success
  // - engine termination status
  // - blackbox evaluation count
  // - optimal   feasible (value, point)
  // - optimal infeasible (value, point)

  return bpy::make_tuple(
    engine_termination_success, 
    engine_termination_status,
    eval_count, 
    best_feasible_solution, 
    best_infeasible_solution);
}

// Exports!

BOOST_PYTHON_MODULE (_nomadlad_bridge) {
  
  // As per the documentation, 
  // the boost::python::numpy environment must be initialized.
  bnp::initialize();

  // :)
  bpy::def("minimize", nomad_minimize_wrapper);

  #ifdef NOMADLAD_VERSION
  bpy::scope().attr("__version__") = std::string(NOMADLAD_VERSION);
  #else
  bpy::scope().attr("__version__") = std::string(__TIMESTAMP__);
  #endif

  #ifdef NOMAD_VERSION_NUMBER
  bpy::scope().attr("__nomad_version__") = std::string(NOMAD_VERSION_NUMBER);
  #else
  bpy::scope().attr("__nomad_version__") = bpy::object();
  #endif
}


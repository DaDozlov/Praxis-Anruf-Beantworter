import 'bootstrap/dist/css/bootstrap.min.css';
import { Rating } from 'react-simple-star-rating';

interface CardProps {
  id: string;
  type: string;
  state: string;
  rating: number;
  lines: { [key: string]: string };
  changeStatus: (status: string, id: string) => void;
  reprocessAudio: (id: string) => void;
  changeRating: (rate: number, id: string) => void;
}

const invertState = (status: string) => {
  return status === 'bearbeitet' ? 'unbearbeitet' : 'bearbeitet';
};

const Card: React.FC<CardProps> = ({
  id,
  type,
  state,
  rating,
  lines,
  changeStatus,
  changeRating,
  reprocessAudio,
}) => {
  return (
    <div className="card">
      <div className="card-header fw-bold">{type}</div>

      <ul className="list-group list-group-flush">
        {Object.entries(lines).map(([key, value]) => (
          <li className="list-group-item" key={key}>
            <div className="row">
              <div className="col-md-2">
                <span className="fw-bold">{key}:</span>
              </div>
              <div className="col-md-10">
                <span>{value}</span>
              </div>
            </div>
          </li>
        ))}

        <li className="list-group-item">
          <div className="row">
            <div className="col-md-2">
              <span className="fw-bold">Audio:</span>
            </div>
            <div className="col-md-10">
              <audio
                controls
                src={`http://127.0.0.1:5000/audio?fileName=${id}`}
              >
                Ihr Browser unterstützt das Audio-Element nicht.
              </audio>
            </div>
          </div>
        </li>

        <li className="list-group-item">
          <div className="row">
            <div className="col-md-2">
              <span className="fw-bold">Qualität der Transkription:</span>
            </div>
            <div className="col-md-10">
              <Rating
                initialValue={rating ?? 0}
                onClick={(rate) => changeRating(rate, id)}
              />
            </div>
          </div>
        </li>
      </ul>

      <div className="card-footer text-muted d-flex justify-content-between">
        <button
          className="btn btn-secondary"
          onClick={() => reprocessAudio(id)}
        >
          Audio erneut verarbeiten
        </button>

        <div className="form-check form-switch">
          <input
            className="form-check-input"
            type="checkbox"
            id="flexSwitchCheckDefault"
            checked={state === 'bearbeitet'}
            onChange={() => changeStatus(invertState(state), id)}
          />
          <label className="form-check-label" htmlFor="flexSwitchCheckDefault">
            {state === 'bearbeitet' ? 'Bearbeitet' : 'Unbearbeitet'}
          </label>
        </div>
      </div>
    </div>
  );
};

export default Card;
